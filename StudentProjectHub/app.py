import os
from flask import Flask, render_template

from config import config_map
from extensions import db, login_manager, migrate
from routes import register_blueprints
from utils.helpers import register_template_filters


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map.get(config_name, config_map["default"]))

    os.makedirs(app.instance_path, exist_ok=True)
    if not app.config.get("S3_BUCKET"):
        os.makedirs(os.path.join(app.config["UPLOAD_ROOT"], "requirements"), exist_ok=True)
        os.makedirs(os.path.join(app.config["UPLOAD_ROOT"], "completed"), exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    register_blueprints(app)
    register_template_filters(app)
    register_error_handlers(app)
    register_context_processors(app)

    from models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


def register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500


def register_context_processors(app):
    @app.context_processor
    def inject_notification_count():
        # Rendered as 0 and immediately corrected client-side by static/js/notifications.js,
        # which fetches /notifications/unread-count on page load and polls every 30s.
        # Avoids a DB query on every single page render for every logged-in user.
        return {"nav_unread_count": 0}
