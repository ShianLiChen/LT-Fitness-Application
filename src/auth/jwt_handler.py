import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g, redirect, url_for, render_template, make_response
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
        token = request.cookies.get("jwt_token")
        if not token:
            header = request.headers.get("Authorization", "")
            parts = header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            return redirect(url_for("user.login_page"))

        try:
            data = decode_token(token)
            user = User.query.get(int(data["sub"]))
            if not user:
                raise Exception("User not found")
        except jwt.ExpiredSignatureError:
            return render_template("error.html", message="Your session has expired. Please log in again.")
        except jwt.InvalidTokenError:
            return render_template("error.html", message="Invalid token. Please log in again.")
        except Exception as e:
            return render_template("error.html", message=str(e))

        g.current_user = user
        g.jwt = data
        return fn(*args, **kwargs)

    return wrapper

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        resp = make_response(view(*args, **kwargs))
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp
    return no_cache
