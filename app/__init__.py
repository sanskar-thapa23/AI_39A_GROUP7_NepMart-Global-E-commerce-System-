from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Instantiate the SQLAlchemy object globally at the very top
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # 1. Core Secret Configurations
    app.config['SECRET_KEY'] = 'dev-secret-key-nepmart'
    
    # 2. MySQL Connection Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:h1elloworld@localhost:3306/nepmart_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 3. Bind the extension to this app instance
    db.init_app(app)
    
    # 4. Import models and execute Table Creation inside the app context
    from app.model.user import User
    
    with app.app_context():
        # This scans your models and creates tables in MySQL if they don't exist
        db.create_all()
    
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