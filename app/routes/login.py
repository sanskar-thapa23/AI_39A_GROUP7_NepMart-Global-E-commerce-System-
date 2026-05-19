from flask import Blueprint

class LoginRoutes:
    def register(self):
        login_bp = Blueprint("login", __name__)

        @login_bp.route("/login")
        def login():
            return "Login Page"

        return login_bp