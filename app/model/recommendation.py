from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class RecommendationEngine:
    def __init__(self, products):
        """
        Initialize the recommendation engine with a list of products.
        Each product should be a dictionary with at least:
        - id
        - name
        - category_display
        - description
        - company
        - specs (dict of properties like packing, certification, etc.)
        """
        self.products = products
        self._prepare_engine()

    def _prepare_engine(self):
        if not self.products:
            self.tfidf_matrix = None
            self.cosine_sim = None
            return

        documents = []
        for p in self.products:
            name = p.get("name", "")
            category = p.get("category_display", "")
            description = p.get("description", "")
            company = p.get("company", "")
            
            # Extract spec values as text
            specs_str = ""
            if isinstance(p.get("specs"), dict):
                specs_str = " ".join([f"{k} {v}" for k, v in p["specs"].items()])
            
            # Combine all text features to represent the product
            doc = f"{name} {category} {description} {company} {specs_str}"
            
            # Preprocess: lowercase and remove extra whitespaces
            doc = re.sub(r'\s+', ' ', doc).strip().lower()
            documents.append(doc)

        # Compute TF-IDF vectors
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.vectorizer.fit_transform(documents)
        
        # Calculate pairwise cosine similarity matrix
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

    def get_recommendations(self, product_id, top_n=3):
        """
        Get the top N recommended products similar to product_id.
        """
        if self.cosine_sim is None:
            return []

        # Find the index of the requested product
        product_idx = None
        for idx, p in enumerate(self.products):
            if p.get("id") == product_id:
                product_idx = idx
                break

        if product_idx is None:
            return []

        # Extract similarity scores for this product index
        sim_scores = list(enumerate(self.cosine_sim[product_idx]))
        
        # Sort products based on similarity scores (descending)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Exclude self and take the top N recommendations
        recommendations = []
        for idx, score in sim_scores:
            if idx == product_idx:
                continue
            recommendations.append(self.products[idx])
            if len(recommendations) == top_n:
                break

        return recommendations
