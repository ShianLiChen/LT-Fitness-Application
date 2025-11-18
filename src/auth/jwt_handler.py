import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g
from config import Config
from models.user import User
from database import db

ALG = "HS256"

def now():
    return datetime.now(timezone.utc)

def create_token(user_id: int, role: str):
    exp = now() + timedelta(minutes=Config.ACCESS_TOKEN_MINUTES)
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": int(now().timestamp()),
        "exp": int(exp.timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm=ALG)

def decode_token(token: str):
    return jwt.decode(token, Config.SECRET_KEY, algorithms=[ALG])

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        parts = header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = parts[1]

        try:
            data = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        user = User.query.get(int(data["sub"]))
        if not user:
            return jsonify({"error": "User not found"}), 401

        g.current_user = user
        g.jwt = data

        return fn(*args, **kwargs)

    return wrapper
