"""
=============================================================
  NepMart — Recommendation Engine (Model)
=============================================================
  OOP: Encapsulation (private matrix), Polymorphism (engine
  swappable), builds TF-IDF on DB products.

  Two recommendation modes:
    1. get_similar(product_id)      — content-based similarity
    2. get_personalized(user_id)    — weighted by view/search history
=============================================================
"""

import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .database import Database


class RecommendationEngine:

    def __init__(self):
        self._products    = []
        self._tfidf_mat   = None
        self._cosine_sim  = None
        self._id_to_idx   = {}
        self._refresh()

    # ── Private: Build TF-IDF Matrix ────────────────────────────

    def _refresh(self):
        """Load all active products from DB and compute the TF-IDF matrix."""
        db = Database()
        rows = db.fetch_all(
            """SELECT p.*, s.company_name AS seller_business_name,
                      s.whatsapp_number, s.company_name AS company
               FROM products p
               JOIN sellers s ON p.seller_id=s.seller_id
               WHERE p.is_active=1 AND p.status='active'"""
        )
        db.close()

        self._products   = list(rows)
        self._id_to_idx  = {p["product_id"]: i for i, p in enumerate(self._products)}

        if not self._products:
            return

        docs = []
        for p in self._products:
            text = " ".join([
                p.get("name", ""),
                p.get("category", ""),
                p.get("description", "") or "",
                p.get("company", "") or "",
            ])
            text = re.sub(r"\s+", " ", text).strip().lower()
            docs.append(text)

        vectorizer      = TfidfVectorizer(stop_words="english")
        self._tfidf_mat = vectorizer.fit_transform(docs)
        self._cosine_sim = cosine_similarity(self._tfidf_mat, self._tfidf_mat)

    # ── Public: Content-based Similar Products ───────────────────

    def get_similar(self, product_id, top_n=6):
        """
        Return top_n products most similar to product_id
        based on TF-IDF cosine similarity.
        """
        if self._cosine_sim is None or product_id not in self._id_to_idx:
            return []

        idx       = self._id_to_idx[product_id]
        scores    = list(enumerate(self._cosine_sim[idx]))
        scores    = sorted(scores, key=lambda x: x[1], reverse=True)

        results = []
        for i, score in scores:
            if i == idx:
                continue
            results.append(self._products[i])
            if len(results) >= top_n:
                break
        return results

    # ── Public: Personalized Recommendations ─────────────────────

    def get_personalized(self, user_id, top_n=8):
        """
        Return top_n personalized recommendations for user_id.
        Uses view_history and search_history to bias the similarity scores.
        """
        if self._cosine_sim is None or not self._products:
            return self._get_fallback(top_n)

        db = Database()

        # Products the user has already viewed
        viewed = db.fetch_all(
            "SELECT DISTINCT product_id FROM view_history WHERE user_id=%s",
            (user_id,)
        )
        viewed_ids = {r["product_id"] for r in viewed}

        # Search terms → find matching products as "seed"
        searches = db.fetch_all(
            "SELECT search_term FROM search_history WHERE user_id=%s ORDER BY searched_at DESC LIMIT 5",
            (user_id,)
        )
        db.close()

        seed_ids = set(viewed_ids)

        for row in searches:
            term = row["search_term"].lower()
            for p in self._products:
                text = f"{p.get('name','')} {p.get('category','')} {p.get('description','') or ''}".lower()
                if term in text:
                    seed_ids.add(p["product_id"])

        if not seed_ids:
            return self._get_fallback(top_n)

        # Aggregate similarity scores from all seed products
        agg = {}
        for seed_id in seed_ids:
            if seed_id not in self._id_to_idx:
                continue
            idx    = self._id_to_idx[seed_id]
            scores = list(enumerate(self._cosine_sim[idx]))
            for i, score in scores:
                pid = self._products[i]["product_id"]
                if pid not in viewed_ids:          # don't re-recommend viewed items
                    agg[pid] = agg.get(pid, 0) + float(score)

        sorted_pids = sorted(agg.items(), key=lambda x: x[1], reverse=True)

        # Persist top scores to DB
        db2 = Database()
        for pid, score in sorted_pids[:top_n]:
            db2.execute(
                """INSERT INTO recommendations (user_id, product_id, recommendation_score)
                   VALUES (%s, %s, %s)
                   ON DUPLICATE KEY UPDATE recommendation_score=%s""",
                (user_id, pid, score, score)
            )
        db2.close()

        result_ids = [pid for pid, _ in sorted_pids[:top_n]]
        return [p for p in self._products if p["product_id"] in result_ids]

    def _get_fallback(self, top_n):
        """When no history exists, return newest products."""
        db = Database()
        rows = db.fetch_all(
            """SELECT p.*, s.company_name AS seller_business_name, s.whatsapp_number
               FROM products p JOIN sellers s ON p.seller_id=s.seller_id
               WHERE p.is_active=1 AND p.status='active' ORDER BY p.created_at DESC LIMIT %s""",
            (top_n,)
        )
        db.close()
        return rows

    # ── History Logging ──────────────────────────────────────────

    @staticmethod
    def log_view(user_id, product_id):
        db = Database()
        db.execute(
            "INSERT INTO view_history (user_id, product_id) VALUES (%s, %s)",
            (user_id, product_id)
        )
        db.close()

    @staticmethod
    def log_search(user_id, search_term):
        if not search_term or not search_term.strip():
            return
        db = Database()
        db.execute(
            "INSERT INTO search_history (user_id, search_term) VALUES (%s, %s)",
            (user_id, search_term.strip()[:255])
        )
        db.close()
