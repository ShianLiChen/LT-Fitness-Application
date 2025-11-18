from flask import Blueprint, render_template, g, make_response
from auth.jwt_handler import jwt_required, nocache
from models.workout import Workout

user_bp = Blueprint("user", __name__)

@user_bp.route("/")
def index():
    return render_template("index.html")

@user_bp.route("/register")
@nocache
def register_page():
    resp = make_response(render_template("register.html"))
    resp.set_cookie("jwt_token", "", expires=0)
    return resp

@user_bp.route("/login")
@nocache
def login_page():
    resp = make_response(render_template("login.html"))
    resp.set_cookie("jwt_token", "", expires=0)
    return resp

@user_bp.get("/dashboard")
@jwt_required
@nocache
def dashboard():
    workouts = Workout.query.filter_by(user_id=g.current_user.id)\
                .order_by(Workout.start_time.desc()).all()

    return render_template(
        "dashboard.html",
        current_user=g.current_user,
        workouts=workouts
    )

@user_bp.get("/profile")
@jwt_required
@nocache
def profile():
    return render_template("profile.html")