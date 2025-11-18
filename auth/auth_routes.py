# auth/auth_routes.py
from flask import Blueprint, request, jsonify
from database import db
from models.user import User
from utils.password_utils import generate_salt, hash_password, verify_password
from auth.jwt_handler import create_token, jwt_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# --------------------
# Register
# --------------------
@auth_bp.post("/register")
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "User already exists"}), 400

    salt = generate_salt()
    password_hash = hash_password(password, salt)

    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        salt=salt
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# --------------------
# Login
# --------------------
@auth_bp.post("/login")
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(password, user.salt, user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(user.id, user.role)

    return jsonify({"token": token, "user": user.to_dict()}), 200


# --------------------
# Protected Route
# --------------------
@auth_bp.get("/me")
@jwt_required
def me():
    from flask import g
    return jsonify({"user": g.current_user.to_dict()}), 200
