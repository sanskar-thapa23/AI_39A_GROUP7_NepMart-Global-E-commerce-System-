from flask import Blueprint
from app.controller.home import MainController
from app.controller.productcontroller import ProductController
 
class MainRoutes:
 
    def __init__(self):
        self.bp = Blueprint("main", __name__)
        self.controller = MainController()
        self.product_controller = ProductController()
        self._register_routes()
 
    def _register_routes(self):
 
        # =========================
        # HOME PAGE
        # =========================
        @self.bp.route("/")
        def home():
            return self.controller.home()
 
        # =========================
        # PRODUCTS LIST PAGE
        # =========================
        @self.bp.route("/products")
        def products():
            return self.product_controller.index()
 
        # =========================
        # SINGLE PRODUCT PAGE
        # =========================
        @self.bp.route("/product/<int:product_id>")
        def product_detail(product_id):
            return self.product_controller.detail(product_id)
 
        # =========================
        # SHOPPING ACTIONS
        # =========================
        @self.bp.route("/cart/add/<int:product_id>", methods=["POST"])
        def add_to_cart(product_id):
            return self.product_controller.add_to_cart(product_id)
 
        @self.bp.route("/wishlist/add/<int:product_id>", methods=["POST"])
        def add_to_wishlist(product_id):
            return self.product_controller.add_to_wishlist(product_id)
 
        # =========================
        # TRADERS LIST PAGE
        # =========================
        @self.bp.route("/traders")
        def traders():
            return self.controller.traders()
 
        # =========================
        # TRADER PROFILE PAGE
        # =========================
        @self.bp.route("/trader/<int:trader_id>")
        def trader_profile(trader_id):
            return self.controller.trader_profile(trader_id)
 
        # =========================
        # DASHBOARD (IMPORTANT)
        # =========================
        @self.bp.route("/dashboard")
        def dashboard():
            return self.controller.dashboard()
 
        # =========================
        # CHECKOUT
        # =========================
        @self.bp.route("/checkout", methods=["POST"])
        def checkout():
            return self.controller.checkout()
 
        # =========================
        # CHAT SYSTEM
        # =========================
        @self.bp.route("/chat", methods=["GET", "POST"])
        def chat():
            return self.controller.chat()
 
    def get_blueprint(self):
        return self.bp
 