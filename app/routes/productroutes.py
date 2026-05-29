
from flask import Blueprint
from app.controller.productcontroller import ProductController


class ProductRoutes:

    def __init__(self):

        self.bp = Blueprint(
            "product",
            __name__,
            url_prefix="/products"
        )

        self.controller = ProductController()

        # Register routes
        self._register_routes()

    def _register_routes(self):

        # =====================================================
        # READ ALL PRODUCTS + SEARCH + SORT + FILTER
        # =====================================================
        @self.bp.route("/", methods=["GET"])
        def index():
            return self.controller.index()

        # =====================================================
        # READ SINGLE PRODUCT
        # =====================================================
        @self.bp.route("/<int:product_id>", methods=["GET"])
        def detail(product_id):
            return self.controller.detail(product_id)

        # =====================================================
        # CREATE PRODUCT
        # =====================================================
        @self.bp.route("/create", methods=["GET", "POST"])
        def create():
            return self.controller.create()

        # =====================================================
        # UPDATE PRODUCT
        # =====================================================
        @self.bp.route(
            "/edit/<int:product_id>",
            methods=["GET", "POST"]
        )
        def edit(product_id):
            return self.controller.edit(product_id)

        # =====================================================
        # DELETE PRODUCT
        # =====================================================
        @self.bp.route(
            "/delete/<int:product_id>",
            methods=["POST"]
        )
        def delete(product_id):
            return self.controller.delete(product_id)

    def get_blueprint(self):
        return self.bp

