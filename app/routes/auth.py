from flask import Blueprint
from app.controller.auth import AuthController


class AuthRoutes:

    def __init__(self):
        self.bp = Blueprint("auth", __name__, url_prefix="/auth")
        self.controller = AuthController()
        self._register_routes()

    def _register_routes(self):

        @self.bp.route("/login", methods=["GET", "POST"])
        def login():
            return self.controller.login()

        @self.bp.route("/register", methods=["GET", "POST"])
        def register():
            return self.controller.register()

        @self.bp.route("/forgot-password", methods=["GET", "POST"])
        def forgot_password():
            return self.controller.forgot_password()

        @self.bp.route("/reset-password/<token>", methods=["GET", "POST"])
        def reset_password(token):
            return self.controller.reset_password(token)

        @self.bp.route("/edit-profile", methods=["GET", "POST"])
        def edit_profile():
            return self.controller.edit_profile()

        @self.bp.route("/dashboard")
        def dashboard():
            return self.controller.dashboard()

        @self.bp.route("/logout")
        def logout():
            return self.controller.logout()

        @self.bp.route("/request-deactivation", methods=["POST"])
        def request_deactivation():
            return self.controller.request_deactivation()

        @self.bp.route("/confirm-deactivation/<token>", methods=["GET", "POST"])
        def confirm_deactivation(token):
            return self.controller.confirm_deactivation(token)

    def get_blueprint(self):
        return self.bp