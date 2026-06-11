import os
from flask import Flask
from app.model.database import Database
import config


def create_app():
    app = Flask(__name__)

    # ── Core Config ───────────────────────────────────────────────
    app.secret_key = config.SECRET_KEY
    app.config.from_object(config)

    # Upload folder
    app.config["UPLOAD_FOLDER"]      = config.UPLOAD_FOLDER
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

    # ── Database: auto-create schema ──────────────────────────────
    try:
        Database.create_tables()
    except Exception as e:
        app.logger.error(f"Database init failed: {e}")
        raise

    # ── Blueprints ────────────────────────────────────────────────
    from app.routes.auth   import AuthRoutes
    from app.routes.home   import MainRoutes
    from app.routes.seller import SellerRoutes
    from app.routes.buyer  import BuyerRoutes

    app.register_blueprint(AuthRoutes().get_blueprint())
    app.register_blueprint(MainRoutes().get_blueprint())
    app.register_blueprint(SellerRoutes().get_blueprint())
    app.register_blueprint(BuyerRoutes().get_blueprint())

    # ── Context processor: cart count available in all templates ──
    from flask import session

    @app.context_processor
    def inject_cart_count():
        count = 0
        if "user_id" in session and session.get("role") in ("buyer", "admin"):
            from app.model.cart import Cart
            try:
                count = Cart.count(session["user_id"])
            except Exception:
                count = 0
        return dict(cart_count=count)

    # ── Teardown ──────────────────────────────────────────────────
    @app.teardown_appcontext
    def close_db(exception=None):
        pass   # PyMySQL connections are per-request in our model

    return app