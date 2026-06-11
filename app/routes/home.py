from flask import Blueprint
from app.controller.home import MainController


class MainRoutes:

    def __init__(self):
        self.bp         = Blueprint("main", __name__)
        self.controller = MainController()
        self._register_routes()

    def _register_routes(self):

        # ── Home ────────────────────────────────────────────────
        @self.bp.route("/")
        def home():
            return self.controller.home()

        # ── Product Catalog ─────────────────────────────────────
        @self.bp.route("/products")
        def products():
            return self.controller.products()

        # ── Product Detail ──────────────────────────────────────
        @self.bp.route("/product/<int:product_id>")
        def product_detail(product_id):
            return self.controller.product_detail(product_id)

        # ── Sellers / Traders Directory ─────────────────────────
        @self.bp.route("/traders")
        def traders():
            return self.controller.traders()

        # ── Seller / Trader Public Profile ──────────────────────
        @self.bp.route("/seller/store/<int:seller_id>")
        def seller_store(seller_id):
            return self.controller.trader_profile(seller_id)

        # Legacy route kept for backward compat
        @self.bp.route("/trader/<int:trader_id>")
        def trader_profile(trader_id):
            return self.controller.trader_profile(trader_id)

    def get_blueprint(self):
        return self.bp