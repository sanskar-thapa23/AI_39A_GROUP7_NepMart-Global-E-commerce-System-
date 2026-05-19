from flask import Flask
from app.routes.auth_routes import AuthRoutes
def create_app():
    app = Flask(__name__)
    auth_routes = AuthRoutes()
    for bp in auth_routes.register():
        app.register_blueprint(bp)
    return app