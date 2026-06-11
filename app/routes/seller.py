from flask import Blueprint
from app.controller.seller_controller import SellerController
from app.services.auth_service import seller_required


class SellerRoutes:

    def __init__(self):
        self.bp         = Blueprint("seller", __name__, url_prefix="/seller")
        self.controller = SellerController()
        self._register_routes()

    def _register_routes(self):

        @self.bp.route("/dashboard")
        @seller_required
        def dashboard():
            return self.controller.dashboard()

        @self.bp.route("/products")
        @seller_required
        def products():
            return self.controller.products()

        @self.bp.route("/product/add", methods=["GET", "POST"])
        @seller_required
        def add_product():
            return self.controller.add_product()

        @self.bp.route("/product/<int:product_id>/edit", methods=["GET", "POST"])
        @seller_required
        def edit_product(product_id):
            return self.controller.edit_product(product_id)

        @self.bp.route("/product/<int:product_id>/delete", methods=["POST"])
        @seller_required
        def delete_product(product_id):
            return self.controller.delete_product(product_id)

        @self.bp.route("/orders")
        @seller_required
        def orders():
            return self.controller.orders()

        @self.bp.route("/order/<int:order_id>/status", methods=["POST"])
        @seller_required
        def update_order_status(order_id):
            return self.controller.update_order_status(order_id)

        @self.bp.route("/analytics")
        @seller_required
        def analytics():
            return self.controller.analytics()

        @self.bp.route("/profile", methods=["GET", "POST"])
        @seller_required
        def profile():
            return self.controller.profile()

    def get_blueprint(self):
        return self.bp
