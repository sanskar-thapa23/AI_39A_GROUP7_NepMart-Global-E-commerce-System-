from flask import Blueprint


class RegisterRoutes:
    def register(self):
        register_bp = Blueprint("register", __name__)

        @register_bp.route("/register")
        def register():
            return "Register Page"

        return register_bp