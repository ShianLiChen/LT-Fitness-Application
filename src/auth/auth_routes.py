# auth/auth_routes.py
from flask import Blueprint, request, jsonify, g, make_response
from database import db
from models.user import User
from utils.password_utils import generate_salt, hash_password, verify_password
from auth.jwt_handler import create_token, jwt_required
from schemas.user_schema import UserSchema
from marshmallow import ValidationError

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
user_schema = UserSchema()

# --------------------
# Register
# --------------------
@auth_bp.post("/register")
def register():
    data = request.get_json()

    try:
        # Validate input
        validated_data = user_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": "Invalid input", "messages": err.messages}), 400

    username = validated_data["username"]
    email = validated_data["email"]
    password = validated_data["password"]

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

    if not user or not verify_password(password, user.salt, user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_token(user.id, user.role)

    # Store token in HTTP-only cookie
    resp = make_response(jsonify({"message": "Login successful", "user": user.to_dict()}))
    resp.set_cookie(
        "jwt_token", token,
        httponly=True,
        secure=False,  # Set to True if using HTTPS
        samesite="Lax",  # or "Strict" depending on your needs
        max_age=60*60  # optional, e.g., 1 hour
    )
    return resp


# --------------------
# Protected Route
# --------------------
@auth_bp.get("/me")
@jwt_required
def me():
    from flask import g
    user = g.current_user
    return jsonify({"user": user_schema.dump(user)})

# --------------------
# Logout (clear cookie)
# --------------------
@auth_bp.post("/logout")
def logout():
    resp = make_response(jsonify({"message": "Successfully logged out"}))
    resp.set_cookie("jwt_token", "", expires=0)  # clear cookie
    return resp

@auth_bp.post("/change-password")
@jwt_required
def change_password():
    from flask import request, g
    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    user = g.current_user

    # Check old password
    if not verify_password(old_password, user.salt, user.password_hash):
        return jsonify({"error": "Current password is incorrect"}), 400

    # Update password using the renamed method
    new_hash = hash_password(new_password, user.salt)  # keep your pepper+salt logic
    user.password_hash = new_hash
    db.session.commit()

    return jsonify({"message": "Password changed successfully"}), 200
