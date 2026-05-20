from flask import Blueprint
from app.controller.home import MainController

class MainRoutes:

    def __init__(self):
        self.bp = Blueprint("main", __name__)
        self.controller = MainController()

    def register(self):

        # 1. Landing / Home route
        self.bp.route("/")(
            self.controller.home
        )

        # 2. Marketplace catalog
        self.bp.route("/products")(
            self.controller.products
        )

        # 3. Product detail specification sheet
        self.bp.route("/product/<int:product_id>")(
            self.controller.product_detail
        )

        # 4. Verified supplier directory search
        self.bp.route("/traders")(
            self.controller.traders
        )

        # 5. Verified supplier storefront profile
        self.bp.route("/trader/<int:trader_id>")(
            self.controller.trader_profile
        )

        # 6. Seller / admin workspace dashboard
        self.bp.route("/dashboard")(
            self.controller.dashboard
        )

        # 7. Direct deal negotiations & live chat panel
        self.bp.route("/chat", methods=["GET", "POST"])(
            self.controller.chat
        )

        return self.bp