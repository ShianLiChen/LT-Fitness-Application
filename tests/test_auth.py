import json
from datetime import datetime, timedelta
from utils.password_utils import verify_password
from models.user import User
from models.password_reset_token import PasswordResetToken

# -------------------------
# Registration Tests
# -------------------------
def test_register_success(client, db):
    payload = {"username": "newuser", "email": "newuser@test.com", "password": "password123"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 201
    assert resp.get_json()["message"] == "User registered successfully"

def test_register_missing_fields(client):
    resp = client.post("/auth/register", json={"username": "user"})
    assert resp.status_code == 400
    assert "Invalid input" in resp.get_json()["error"]

def test_register_existing_user(client, test_user):
    payload = {"username": "testuser", "email": "test@test.com", "password": "secret"}
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400
    assert "User already exists" in resp.get_json()["error"]


# -------------------------
# Login Tests
# -------------------------
def test_login_success(client, test_user):
    payload = {"username": "testuser", "password": "secret"}
    resp = client.post("/auth/login", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["user"]["username"] == "testuser"
    assert "csrf_token" in data

def test_login_missing_fields(client):
    resp = client.post("/auth/login", json={"username": ""})
    assert resp.status_code == 400
    assert "Missing username or password" in resp.get_json()["error"]

def test_login_invalid_credentials(client):
    resp = client.post("/auth/login", json={"username": "nonexistent", "password": "wrong"})
    assert resp.status_code == 401


# -------------------------
# Protected User Info Tests
# -------------------------
def test_me_protected(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.get_json()["user"]["username"] == test_user.username

def test_me_unauthorized(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


# -------------------------
# Change Password Tests
# -------------------------
def test_change_password_success(client, test_user, auth_headers, db):
    headers = auth_headers(test_user.id)
    payload = {"old_password": "secret", "new_password": "newsecret"}
    resp = client.post("/auth/change-password", json=payload, headers=headers)
    assert resp.status_code == 200
    db_user = User.query.get(test_user.id)
    assert verify_password("newsecret", db_user.password_hash)

def test_change_password_incorrect_old(client, test_user, auth_headers):
    headers = auth_headers(test_user.id)
    payload = {"old_password": "wrong", "new_password": "newpass"}
    resp = client.post("/auth/change-password", json=payload, headers=headers)
    assert resp.status_code == 400
    assert "Current password is incorrect" in resp.get_json()["error"]


# -------------------------
# Forgot Password & Reset Password Tests
# -------------------------
def test_forgot_password_no_email(client):
    resp = client.post("/auth/forgot-password", json={})
    assert resp.status_code == 400
    assert "Email is required" in resp.get_json()["error"]

def test_forgot_password_nonexistent_email(client):
    resp = client.post("/auth/forgot-password", json={"email": "missing@test.com"})
    assert resp.status_code == 200
    assert "reset link has been sent" in resp.get_json()["message"]

def test_reset_password_success(client, test_user, db):
    token_str = "testtoken123"
    token = PasswordResetToken(
        user_id=test_user.id,
        token=token_str,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.session.add(token)
    db.session.commit()

    payload = {"token": token_str, "new_password": "newpass123"}
    resp = client.post("/auth/reset-password", json=payload)
    assert resp.status_code == 200

    db_user = User.query.get(test_user.id)
    from utils.password_utils import verify_password
    assert verify_password("newpass123", db_user.password_hash)

    db.session.refresh(token)
    assert token.used

def test_reset_password_invalid_token(client):
    payload = {"token": "invalid", "new_password": "pass"}
    resp = client.post("/auth/reset-password", json=payload)
    assert resp.status_code == 400
    assert "Token expired or invalid" in resp.get_json()["error"]

def test_reset_password_missing_fields(client):
    resp = client.post("/auth/reset-password", json={"token": "abc"})
    assert resp.status_code == 400
    assert "Token and new password are required" in resp.get_json()["error"]
