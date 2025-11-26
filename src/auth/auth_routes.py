# auth/auth_routes.py
from flask import Blueprint, request, jsonify, make_response, render_template
from database import db
from models.user import User
from utils.password_utils import hash_password, verify_password
from schemas.user_schema import UserSchema
from marshmallow import ValidationError
from auth.jwt_handler import csrf_protect
import uuid
from datetime import datetime, timedelta
from flask import current_app
from flask_mail import Message
from models.password_reset_token import PasswordResetToken

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
@csrf_protect
def logout():
    resp = make_response(jsonify({"message": "Successfully logged out"}))
    unset_jwt_cookies(resp)
    return resp

# --------------------
# Change Password
# --------------------
@auth_bp.post("/change-password")
@jwt_required()
@csrf_protect
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

# --------------------
# Forgot Password: Request Reset
# --------------------
@auth_bp.post("/forgot-password")
def forgot_password():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal that email doesn't exist
        return jsonify({"message": "If this email exists, a reset link has been sent"}), 200

    # Generate token
    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=1)

    reset_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
    db.session.add(reset_token)
    db.session.commit()

    # Send email - change domain for actual deployment
    reset_url = f"http://127.0.0.1:5000/auth/reset-password?token={token}"
    msg = Message(
        "Reset Your Password",
        sender="cscifitnessproject@gmail.com",
        recipients=[user.email]
    )
    msg.body = f"Click the link to reset your password:\n\n{reset_url}\n\nThis link expires in 1 hour."
    current_app.mail.send(msg)

    return jsonify({"message": "If this email exists, a reset link has been sent"}), 200


# --------------------
# Reset Password: Submit New Password
# --------------------
@auth_bp.post("/reset-password")
def reset_password():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token or reset_token.used or reset_token.expires_at < datetime.utcnow():
        return jsonify({"error": "Token expired or invalid"}), 400

    user = User.query.get(reset_token.user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update password
    user.password_hash = hash_password(new_password)
    reset_token.used = True
    db.session.commit()

    return jsonify({"message": "Password has been reset successfully"}), 200

# Show forgot password form
@auth_bp.get("/forgot-password")
def forgot_password_page():
    return render_template("forgot_password.html")

# Show reset password form
@auth_bp.get("/reset-password")
def reset_password_page():
    token = request.args.get("token")
    if not token:
        return "Invalid reset link", 400
    return render_template("reset_password.html", token=token)