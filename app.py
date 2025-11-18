from flask import Flask
from config import Config
from database import db

# Import blueprints
from auth import auth_bp
from routes.user_routes import user_bp

def create_app():
    app = Flask(__name__)
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
