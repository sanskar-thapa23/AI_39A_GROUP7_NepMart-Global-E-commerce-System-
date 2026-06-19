from flask import Blueprint
from app.controller.admincontroller import AdminController
from app.auth import admin_required

class AdminRoutes:
    def __init__(self):
        self.bp = Blueprint("admin", __name__, url_prefix="/admin")
        self.controller = AdminController()
        self._register_routes()

    def _register_routes(self):
        # Apply admin_required decorator for role-based access control
        @self.bp.route("/")
        @admin_required
        def index():
            return self.controller.index()

        @self.bp.route("/user/edit/<int:user_id>", methods=["GET", "POST"])
        @admin_required
        def edit_user(user_id):
            return self.controller.edit_user(user_id)

        @self.bp.route("/user/delete/<int:user_id>", methods=["POST"])
        @admin_required
        def delete_user(user_id):
            return self.controller.delete_user(user_id)

    def get_blueprint(self):
        return self.bp