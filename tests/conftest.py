import sys
import os
# Add src folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
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
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",  # in-memory DB
        "JWT_TOKEN_LOCATION": ["headers"],
        "JWT_COOKIE_CSRF_PROTECT": False,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key"
    }

    app = create_app(test_config=test_config)  # <- pass test_config

    with app.app_context():
        _db.create_all()  # create tables in SQLite
        yield app.test_client()
        _db.session.remove()
        _db.drop_all()  # drop tables in SQLite only



# -------------------------
# Database Fixture
# -------------------------
@pytest.fixture
def db(client):
    return _db


# -------------------------
# Auth Headers Fixture
# -------------------------
@pytest.fixture
def auth_headers(client, db):
    """
    Return Authorization header for a given user ID.
    Usage:
        headers = auth_headers(test_user.id)
        client.get("/recipes/", headers=headers)
    """
    def _make_headers(user_id):
        token = create_access_token(identity=str(user_id))
        return {"Authorization": f"Bearer {token}"}
    return _make_headers


# -------------------------
# Test Users
# -------------------------
@pytest.fixture
def test_user(db):
    user = User(
        username="testuser",
        email="test@test.com",
        password_hash=hash_password("secret")
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def second_user(db):
    user = User(
        username="seconduser",
        email="second@test.com",
        password_hash=hash_password("password123")
    )
    db.session.add(user)
    db.session.commit()
    return user
