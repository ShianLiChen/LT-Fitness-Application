from flask import Flask
from config import Config
from database import db
import os

# Import blueprints
from auth import auth_bp
from routes.user_routes import user_bp

def create_app():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "templates"),
        static_folder=os.path.join(project_root, "static")
    )
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
