from flask import Blueprint
from app.controller.home import MainController

class MainRoutes:

    def __init__(self):
        self.bp = Blueprint("main", __name__)
        self.controller = MainController()
        self._register_routes()

    def _register_routes(self):

        self.bp.route("/")(self.controller.home)

        self.bp.route("/products")(self.controller.products)

        self.bp.route("/product/<int:product_id>")(self.controller.product_detail)

        self.bp.route("/traders")(self.controller.traders)

        self.bp.route("/trader/<int:trader_id>")(self.controller.trader_profile)

        self.bp.route("/dashboard")(self.controller.dashboard)

        self.bp.route("/chat", methods=["GET", "POST"])(self.controller.chat)

    def get_blueprint(self):
        return self.bp