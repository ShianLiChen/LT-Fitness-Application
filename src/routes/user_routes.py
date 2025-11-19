# user_routes.py
from flask import Blueprint, render_template, redirect, url_for, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.workout import Workout
from auth.jwt_handler import nocache  # your no-cache decorator

user_bp = Blueprint("user", __name__)

# --------------------
# Index / Home Page
# --------------------
@user_bp.route("/")
def index():
    return render_template("index.html")

# --------------------
# Register Page
# --------------------
@user_bp.route("/register")
@nocache
def register_page():
    resp = make_response(render_template("register.html"))
    # Clear JWT cookie if present
    resp.set_cookie("access_token_cookie", "", expires=0, httponly=True, samesite="Lax")
    return resp


# --------------------
# Login Page
# --------------------
@user_bp.route("/login")
@nocache
def login_page():
    resp = make_response(render_template("login.html"))
    # Clear JWT cookie to log out user on visit
    resp.set_cookie("access_token_cookie", "", expires=0, httponly=True, samesite="Lax")
    return resp


# --------------------
# Dashboard Page
# --------------------
@user_bp.get("/dashboard")
@jwt_required()
@nocache
def dashboard():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)

    if not current_user:
        # Redirect to login if user not found
        return redirect(url_for("user.login_page"))

    workouts = Workout.query.filter_by(user_id=user_id)\
                .order_by(Workout.start_time.desc()).all()

    return render_template(
        "dashboard.html",
        current_user=current_user,
        workouts=workouts
    )


# --------------------
# Profile Page
# --------------------
@user_bp.get("/profile")
@jwt_required()
@nocache
def profile():
    user_id = get_jwt_identity()
    current_user = User.query.get(user_id)

    if not current_user:
        # Redirect to login if user not found
        return redirect(url_for("user.login_page"))

    return render_template(
        "profile.html",
        current_user=current_user
    )
