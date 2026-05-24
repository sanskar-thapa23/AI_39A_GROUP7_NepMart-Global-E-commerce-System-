from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.model.database import Database
# Instantiate the SQLAlchemy object globally at the very top
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    database=Database()
    
    
    # 5. Deferred Route Imports (completely safe from circular dependencies)
    from app.routes.auth import AuthRoutes
    from app.routes.home import MainRoutes  # Moved down here inside the function context
    
    # Register Auth Blueprint
    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.get_blueprint())

    # Register Home/Main Blueprint
    main_routes = MainRoutes()
    app.register_blueprint(main_routes.register())

    return app