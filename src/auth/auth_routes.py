# auth/auth_routes.py
from flask import Blueprint, request, jsonify, make_response
from database import db
from models.user import User
from utils.password_utils import hash_password, verify_password
from schemas.user_schema import UserSchema
from marshmallow import ValidationError

# Flask-JWT-Extended
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    set_access_cookies,
    unset_jwt_cookies,
    get_csrf_token
)

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
user_schema = UserSchema()

# --------------------
# Register
# --------------------
@auth_bp.post("/register")
def register():
    data = request.get_json()

    try:
        validated_data = user_schema.load(data)
    except ValidationError as e:
        # Combine all field errors into one string
        errors = []
        for field, msgs in e.messages.items():
            for msg in msgs:
                errors.append(f"{field}: {msg}")
        error_str = "; ".join(errors)
        return jsonify({"error": f"Invalid input: {error_str}"}), 400

    username = validated_data["username"]
    email = validated_data["email"]
    password = validated_data["password"]

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "User already exists"}), 400

    password_hash = hash_password(password)

    user = User(
        username=username,
        email=email,
        password_hash=password_hash
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
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid credentials"}), 401

    # Create JWT
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    # Get CSRF token for frontend
    csrf_token = get_csrf_token(access_token)

    # Response with JWT cookie + CSRF token
    resp = make_response(jsonify({
        "message": "Login successful",
        "user": user.to_dict(),
        "csrf_token": csrf_token  # frontend must send this in X-CSRF-TOKEN header
    }))
    set_access_cookies(resp, access_token)

    return resp


# --------------------
# Protected Route: GET /me
# --------------------
@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"user": user_schema.dump(user)})


# --------------------
# Get CSRF token for frontend
# --------------------
@auth_bp.get("/csrf-token")
@jwt_required()  # ensures the JWT cookie is present
def csrf_token_route():
    # Get the JWT from cookies automatically
    access_token = request.cookies.get('access_token_cookie')  # default name for set_access_cookies
    if not access_token:
        return jsonify({"error": "JWT not found"}), 401

    csrf = get_csrf_token(encoded_token=access_token)
    return jsonify({"csrf_token": csrf})

# --------------------
# Logout
# --------------------
@auth_bp.post("/logout")
@jwt_required()
def logout():
    resp = make_response(jsonify({"message": "Successfully logged out"}))
    unset_jwt_cookies(resp)
    return resp

# --------------------
# Change Password
# --------------------
@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not verify_password(old_password, user.password_hash):
        return jsonify({"error": "Current password is incorrect"}), 400

    user.password_hash = hash_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password changed successfully"})
