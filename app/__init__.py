from flask import Flask, render_template

from config import Config
from app.extensions import db, migrate, login_manager


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Temporary user loader for Week 1.
    # Kiên/Auth module sẽ thay bằng User.query.get(...) sau.
    @login_manager.user_loader
    def load_user(user_id):
        return None

    from app.auth import auth_bp
    from app.shop import shop_bp
    from app.admin import admin_bp
    from app.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    @app.route("/")
    def home():
        return render_template("home.html")

    return app