from flask import Blueprint
from app.controller.vendorcontroller import VendorController

class VendorRoutes:

    def __init__(self):
        self.bp = Blueprint("vendor", __name__, url_prefix="/vendor")
        self.controller = VendorController()
        self._register_routes()

    def _register_routes(self):

        @self.bp.route("/dashboard")
        def dashboard():
            return self.controller.dashboard()

        @self.bp.route("/products")
        def products():
            return self.controller.products()

        @self.bp.route("/orders")
        def orders():
            return self.controller.orders()

        @self.bp.route("/analytics")
        def analytics():
            return self.controller.analytics()

        @self.bp.route("/messages")
        def messages():
            return self.controller.messages()
            
        @self.bp.route("/order/process/<int:order_id>", methods=["POST"])
        def process_order(order_id):
            return self.controller.process_order(order_id)

        @self.bp.route("/order/details/<int:order_id>")
        def order_details(order_id):
            return self.controller.order_details(order_id)

    def get_blueprint(self):
        return self.bp