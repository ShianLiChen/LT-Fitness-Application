from flask import Blueprint, render_template

user_bp = Blueprint("user", __name__)

@user_bp.route("/")
def index():
    return render_template("index.html")

@user_bp.route("/register")
def register_page():
    return render_template("register.html")

@user_bp.route("/login")
def login_page():
    return render_template("login.html")
