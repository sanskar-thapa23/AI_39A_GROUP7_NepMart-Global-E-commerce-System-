from flask import Blueprint
from app.controller.buyer_controller import BuyerController


class BuyerRoutes:

    def __init__(self):
        self.bp         = Blueprint("buyer", __name__, url_prefix="/buyer")
        self.controller = BuyerController()
        self._register_routes()

    def _register_routes(self):

        @self.bp.route("/cart")
        def cart():
            return self.controller.view_cart()

        @self.bp.route("/cart/add/<int:product_id>", methods=["POST"])
        def add_to_cart(product_id):
            return self.controller.add_to_cart(product_id)

        @self.bp.route("/cart/remove/<int:product_id>", methods=["POST"])
        def remove_from_cart(product_id):
            return self.controller.remove_from_cart(product_id)

        @self.bp.route("/cart/update", methods=["POST"])
        def update_cart():
            return self.controller.update_cart()

        @self.bp.route("/checkout", methods=["GET", "POST"])
        def checkout():
            return self.controller.checkout()

        @self.bp.route("/orders")
        def orders():
            return self.controller.my_orders()

    def get_blueprint(self):
        return self.bp
