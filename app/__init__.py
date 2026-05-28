from flask import Flask
from app.model.database import Database
import config

def create_app():
    app = Flask(__name__)
    # Initialize MySQL connection (PyMySQL)
    app.secret_key = config.SECRET_KEY
    database = Database()
    app.db = database  # optional global access

    # Import routes (avoid circular import)
    from app.routes.auth import AuthRoutes
    from app.routes.home import MainRoutes

    # Register blueprints
    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.get_blueprint())

    main_routes = MainRoutes()
    app.register_blueprint(main_routes.get_blueprint())

    return app