from flask import Flask
from app.routes.auth_routes import AuthRoutes
def create_app():
    app = Flask(__name__)
<<<<<<< HEAD
    
    # 1. Core Secret Configurations
    app.config['SECRET_KEY'] = 'dev-secret-key-nepmart'
    
    # 2. MySQL Connection Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://nepmart:Qlz%409766@localhost/nepmart"
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
=======
>>>>>>> 9b87d3591c8f836f307b88328b9ab6fea493e78d
    auth_routes = AuthRoutes()
    for bp in auth_routes.register():
        app.register_blueprint(bp)
    return app