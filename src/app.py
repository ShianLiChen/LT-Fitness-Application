from flask import Flask, render_template
from config import Config
from database import db
import os

# Import blueprints
from auth import auth_bp
from routes.user_routes import user_bp
from routes.workout_routes import workout_bp
from routes.recipe_routes import recipe_bp
from routes.stats_routes import stats_bp

from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer

# Flask-JWT-Extended
from flask_jwt_extended import JWTManager


# -------------------------
# Application Factory
# -------------------------
def create_app(test_config=None):
    """
    Create and configure the Flask application.
    """

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "templates"),
        static_folder=os.path.join(project_root, "static")
    )

    # Load configuration
    if test_config:
        app.config.update(test_config)
    else:
        app.config.from_object(Config)

    # -------------------------
    # Initialize Extensions
    # -------------------------
    db.init_app(app)
    jwt = JWTManager(app)
    mail = Mail(app)
    app.mail = mail
    app.serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    # -------------------------
    # Register Blueprints
    # -------------------------
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(workout_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(stats_bp)

    # -------------------------
    # JWT Error Handlers
    # -------------------------
    @jwt.unauthorized_loader
    def handle_missing_token(err):
        return render_template(
            "error.html",
            message="You must be logged in to access this page."
        ), 401

    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return render_template(
            "error.html",
            message="Session expired. Please log in again."
        ), 401

    @jwt.invalid_token_loader
    def handle_invalid_token(err):
        return render_template(
            "error.html",
            message="Invalid token. Please log in again."
        ), 401

    return app


# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", debug=True)
