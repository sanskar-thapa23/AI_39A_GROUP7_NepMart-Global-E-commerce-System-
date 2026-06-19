from flask import Flask
from flask_mail import Mail
from app.model.database import Database
import config

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = config.SECRET_KEY
    
    # Load Mail Configuration (Ensure these exist in your config.py)
    app.config['MAIL_SERVER'] = getattr(config, 'MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = getattr(config, 'MAIL_PORT', 587)
    app.config['MAIL_USE_TLS'] = getattr(config, 'MAIL_USE_TLS', True)
    app.config['MAIL_USERNAME'] = getattr(config, 'MAIL_USERNAME', None)
    app.config['MAIL_PASSWORD'] = getattr(config, 'MAIL_PASSWORD', None)
    app.config['MAIL_DEFAULT_SENDER'] = getattr(config, 'MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

    # Initialize Extensions
    mail = Mail(app)
    database = Database()

    # Create tables if they don't exist on startup
    Database.create_tables()

    # Import routes (avoid circular import)
    from app.routes.auth import AuthRoutes
    from app.routes.home import MainRoutes
    from app.routes.vendor import VendorRoutes
    from app.routes.productroutes import ProductRoutes
    from app.routes.adminroutes import AdminRoutes
    # Register blueprints
    auth_routes = AuthRoutes()
    app.register_blueprint(auth_routes.get_blueprint())

    main_routes = MainRoutes()
    app.register_blueprint(main_routes.get_blueprint())
    product_routes=ProductRoutes()
    app.register_blueprint(product_routes.get_blueprint())
    vendor_routes = VendorRoutes()
    app.register_blueprint(vendor_routes.get_blueprint())

    admin_routes = AdminRoutes()
    app.register_blueprint(admin_routes.get_blueprint())
    return app