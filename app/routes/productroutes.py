# app/routes/product_routes.py
from flask import Blueprint
from app.controller.productcontroller import ProductController

class ProductRoutes:
    def __init__(self):
        # The first parameter string MUST match your template name prefix exactly
        self.bp = Blueprint("products", __name__, url_prefix="/products")
        self.controller = ProductController()
        self._register_routes()

    def _register_routes(self):
        @self.bp.route("/")
        def index():
            return self.controller.index()

        @self.bp.route("/create", methods=["GET", "POST"])
        def create():
            return self.controller.create()

        @self.bp.route("/edit/<int:product_id>", methods=["GET", "POST"])
        def edit(product_id):
            return self.controller.edit(product_id)

        @self.bp.route("/delete/<int:product_id>", methods=["POST"])
        def delete(product_id):
            return self.controller.delete(product_id)

    def get_blueprint(self):
        return self.bp