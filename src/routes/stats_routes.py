# src/routes/stats_routes.py
from flask import Blueprint, jsonify, render_template
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")


# -------------------------
# UI ROUTES
# -------------------------

@stats_bp.route("/ui", methods=["GET"])
def stats_page():
    """
    Render the stats page for the logged-in user.
    Requires a valid JWT cookie; otherwise, redirects to login page.
    """
    try:
        # Check if user is logged in via cookie
        verify_jwt_in_request(locations=['cookies'])

        # Fetch User to populate the Navbar
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        # Pass current_user=user so base.html knows we are logged in
        return render_template("stats.html", current_user=user)
    except Exception:
        # If not logged in, show the login page
        return render_template("login.html", error="Please login first")


# -------------------------
# API ROUTES
# -------------------------

@stats_bp.route("/api/data", methods=["GET"])
@jwt_required()
def get_stats_data():
    """
    Return JSON data for charts showing the last 7 days of:
    - Calories burned from workouts
    - Calories consumed from recipes
    - Total macros (protein, carbs, fats)
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    # Calculate dates for the last 7 days
    today = datetime.utcnow().date()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    # Initialize data structures
    labels = [d.strftime("%a %m/%d") for d in dates]
    calories_burned_data = [0] * 7
    calories_consumed_data = [0] * 7
    total_macros = {"protein": 0, "carbs": 0, "fats": 0}

    # Process workouts (calories burned)
    for workout in user.workouts:
        if workout.start_time:
            w_date = workout.start_time.date()
            if w_date in dates:
                index = dates.index(w_date)
                calories_burned_data[index] += (workout.calories_burned or 0)

    # Process recipes (macros consumed)
    for recipe in user.recipes:
        if recipe.created_at:
            r_date = recipe.created_at.date()
            if r_date in dates:
                index = dates.index(r_date)
                calories_consumed_data[index] += (recipe.calories or 0)

                total_macros["protein"] += (recipe.protein or 0)
                total_macros["carbs"] += (recipe.carbs or 0)
                total_macros["fats"] += (recipe.fats or 0)

    return jsonify({
        "labels": labels,
        "burned": calories_burned_data,
        "consumed": calories_consumed_data,
        "macros": total_macros
    })
