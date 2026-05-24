from flask import Blueprint
from app.controller.auth import AuthController


class AuthRoutes:

    def __init__(self):
        self.bp = Blueprint("auth", __name__,url_prefix="/auth")
        self.controller = AuthController()

        # register routes
        self._register_routes()

    def _register_routes(self):

        @self.bp.route("/login", methods=["GET", "POST"])
        def login():
            return self.controller.login()

        @self.bp.route("/register", methods=["GET", "POST"])
        def register():
            return self.controller.register()

    def get_blueprint(self):
        return self.bp