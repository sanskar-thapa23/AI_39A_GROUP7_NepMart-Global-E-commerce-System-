from flask import Flask
from app.model.database import Database
import config


def create_app():
    app = Flask(__name__)

    # --- Core config ---
    app.secret_key = config.SECRET_KEY
    # Pull anything else you defined in config.py
    app.config.from_object(config)

    # --- Database (PyMySQL wrapper) ---
    try:
        app.db = Database()
    except Exception as e:
        app.logger.error(f"Database init failed: {e}")
        raise

    # --- Blueprints (deferred imports to avoid circulars) ---
    from app.routes.auth import AuthRoutes
    from app.routes.home import MainRoutes

    app.register_blueprint(AuthRoutes().get_blueprint())
    app.register_blueprint(MainRoutes().get_blueprint())

    # --- Teardown: close DB connection per request context ---
    @app.teardown_appcontext
    def close_db(exception=None):
        db = getattr(app, "db", None)
        if db and hasattr(db, "close"):
            try:
                db.close()
            except Exception:
                pass

    return app