"""
=============================================================
  NepMart — Main / Home Controller
=============================================================
  Landing page, product browsing, trader directory.
  All data fetched dynamically from MySQL.
=============================================================
"""

from flask import render_template, abort, request, session

from app.model.product import Product
from app.model.seller import Seller
from app.model.recommendation import RecommendationEngine


# Singleton recommendation engine (built once per process)
_rec_engine = None


def get_rec_engine():
    global _rec_engine
    if _rec_engine is None:
        _rec_engine = RecommendationEngine()
    return _rec_engine


class MainController:

    # ── HOME PAGE ────────────────────────────────────────────────

    def home(self):
        engine   = get_rec_engine()
        user_id  = session.get("user_id")

        featured   = Product.get_all_active(limit=6)
        trending   = Product.get_trending(limit=6)
        categories = Product.get_categories()

        recommended = []
        if user_id:
            recommended = engine.get_personalized(user_id, top_n=8)
        else:
            recommended = engine._get_fallback(8)

        return render_template(
            "landing_page.html",
            active_page="home",
            featured_products=featured,
            trending_products=trending,
            recommended_products=recommended,
            categories=categories,
        )

    # ── PRODUCTS LIST ────────────────────────────────────────────

    def products(self):
        search_query      = request.args.get("search", "").strip()
        selected_category = request.args.get("category", "").strip()
        user_id           = session.get("user_id")

        # Log search history for logged-in users
        if user_id and search_query:
            RecommendationEngine.log_search(user_id, search_query)

        if search_query or selected_category:
            products = Product.search(search_query, selected_category or None)
        else:
            products = Product.get_all_active()

        categories = Product.get_categories()

        return render_template(
            "products.html",
            products=products,
            active_page="products",
            search_query=search_query,
            selected_category=selected_category,
            categories=categories,
        )

    # ── PRODUCT DETAIL ───────────────────────────────────────────

    def product_detail(self, product_id):
        product = Product.get_by_id(product_id)
        if not product:
            abort(404)

        # Log view history for logged-in users
        user_id = session.get("user_id")
        if user_id:
            RecommendationEngine.log_view(user_id, product_id)

        # Similar products
        engine  = get_rec_engine()
        similar = engine.get_similar(product_id, top_n=4)

        # Build WhatsApp URL
        wa_number  = (product.get("whatsapp_number") or "").strip().replace(" ", "")
        wa_message = f"Hello, I am interested in your product: {product['name']}"
        wa_url     = f"https://wa.me/{wa_number}?text={wa_message}" if wa_number else None

        return render_template(
            "product_detail.html",
            product=product,
            similar_products=similar,
            wa_url=wa_url,
            active_page="products",
        )

    # ── TRADERS DIRECTORY ────────────────────────────────────────

    def traders(self):
        search_query         = request.args.get("search", "").strip().lower()
        selected_business_type = request.args.get("business_type", "").strip()

        sellers = Seller.get_all_with_user()

        if search_query:
            sellers = [
                s for s in sellers
                if search_query in s.get("company_name", "").lower()
                or search_query in s.get("full_name", "").lower()
            ]

        return render_template(
            "traders.html",
            traders=sellers,
            active_page="traders",
            search_query=search_query,
            selected_business_type=selected_business_type,
        )

    # ── TRADER / SELLER PROFILE ──────────────────────────────────

    def trader_profile(self, seller_id):
        seller = Seller.get_with_user(seller_id)
        if not seller:
            abort(404)

        listed_products = Product.get_by_seller(seller_id)

        wa_number = (seller.get("whatsapp_number") or "").strip().replace(" ", "")
        wa_url    = f"https://wa.me/{wa_number}" if wa_number else None

        return render_template(
            "trader_profile.html",
            trader=seller,
            listed_products=listed_products,
            wa_url=wa_url,
            active_page="traders",
        )