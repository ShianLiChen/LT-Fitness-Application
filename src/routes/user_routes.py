from flask import Blueprint, render_template, g, make_response
from auth.jwt_handler import jwt_required, nocache

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
    # For now, keep it simple
    stats = {}  # or any dummy stats for testing
    resp = make_response(render_template("dashboard.html", current_user=g.current_user, stats=stats))
    
    # Add headers to prevent caching
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    
    return resp