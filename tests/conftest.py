import os
import sys

# Add src folder to sys.path **before imports** to ensure modules can be found
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from database import db as _db
from models.user import User
from utils.password_utils import hash_password


# -------------------------
# Flask Test Client Fixture
# -------------------------
@pytest.fixture
def client():
    """
    Create and configure a Flask test client for use in tests.

    Uses an in-memory SQLite database to isolate tests and ensure
    that changes do not persist between test runs.

    Returns:
        FlaskClient: A test client instance for making HTTP requests.
    """
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_TOKEN_LOCATION": ["headers"],
        "JWT_COOKIE_CSRF_PROTECT": False,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    }

    # Initialize the Flask app with the test configuration
    app = create_app(test_config=test_config)

    # Set up the application context and initialize the database
    with app.app_context():
        _db.create_all()  # Create all tables in the in-memory DB
        yield app.test_client()  # Provide the test client to the test
        _db.session.remove()  # Clean up the session
        _db.drop_all()  # Drop tables to reset DB state


# -------------------------
# Database Fixture
# -------------------------
@pytest.fixture
def db(client):
    """
    Provide access to the database object for tests.

    Args:
        client: The Flask test client fixture.

    Returns:
        SQLAlchemy: The database object (_db) used in the app.
    """
    return _db


# -------------------------
# Auth Headers Fixture
# -------------------------
@pytest.fixture
def auth_headers(client, db):
    """
    Factory fixture to generate Authorization headers for a given user ID.

    This allows tests to make authenticated requests without manually
    creating JWT tokens each time.

    Usage:
        headers = auth_headers(test_user.id)
        client.get("/recipes/", headers=headers)

    Returns:
        function: A function that takes user_id and returns auth headers.
    """
    def _make_headers(user_id):
        token = create_access_token(identity=str(user_id))
        return {"Authorization": f"Bearer {token}"}

    return _make_headers


# -------------------------
# Test User Fixtures
# -------------------------
@pytest.fixture
def test_user(db):
    """
    Create a sample user for testing purposes.

    This fixture adds a user to the test database and commits the session.

    Returns:
        User: The created test user object.
    """
    user = User(
        username="testuser",
        email="test@test.com",
        password_hash=hash_password("secret"),
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def second_user(db):
    """
    Create a second sample user for tests that require multiple users.

    Returns:
        User: The created second test user object.
    """
    user = User(
        username="seconduser",
        email="second@test.com",
        password_hash=hash_password("password123"),
    )
    db.session.add(user)
    db.session.commit()
    return user
