# src/routes/workout_routes.py
from flask import Blueprint, request, jsonify, render_template
from database import db
from models.workout import Workout
from models.user import User
from schemas.workout_schema import WorkoutSchema
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime
from auth.jwt_handler import csrf_protect
import requests
import os
import json


workout_bp = Blueprint("workout", __name__, url_prefix="/workouts")
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)


# -------------------------
# CRUD ROUTES
# -------------------------

@workout_bp.post("/")
@jwt_required()
@csrf_protect
def create_workout():
    """
    Create a new workout for the logged-in user.
    Automatically calculates duration and estimates calories if missing.
    """
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    try:
        validated = workout_schema.load(data)
    except Exception as e:
        return jsonify({"error": "Invalid input", "messages": getattr(e, "messages", str(e))}), 400

    start_time = validated.get("start_time", datetime.utcnow())
    end_time = validated.get("end_time")

    # Calculate duration if not provided
    duration_calc = validated.get("duration_minutes")
    if duration_calc is None:
        if start_time and end_time:
            duration_calc = (end_time - start_time).total_seconds() / 60
        else:
            duration_calc = 30.0  # Default to 30 mins

    # Estimate calories if missing
    calories = validated.get("calories_burned")
    if calories is None:
        calories = int(duration_calc * 6)  # Approx 6 calories per minute

    workout = Workout(
        user_id=user.id,
        exercise_name=validated["exercise_name"],
        start_time=start_time,
        end_time=end_time,
        duration_minutes=duration_calc,
        sets=validated.get("sets"),
        reps=validated.get("reps"),
        weight_lbs=validated.get("weight_lbs"),
        machine=validated.get("machine"),
        calories_burned=calories,
        notes=validated.get("notes")
    )

    db.session.add(workout)
    db.session.commit()
    return jsonify({"message": "Workout created", "workout": workout.to_dict()}), 201


@workout_bp.get("/")
@jwt_required()
def get_workouts():
    """
    Retrieve all workouts for the logged-in user.
    """
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"workouts": workouts_schema.dump(user.workouts)}), 200


@workout_bp.get("/<int:id>")
@jwt_required()
def get_workout(id):
    """
    Retrieve a single workout by ID for the logged-in user.
    """
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 400

    workout = Workout.query.filter_by(id=id, user_id=user_id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404

    return jsonify({"workout": workout_schema.dump(workout)}), 200


@workout_bp.put("/<int:id>")
@jwt_required()
@csrf_protect
def update_workout(id):
    """
    Update an existing workout by ID for the logged-in user.
    """
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 400

    workout = Workout.query.filter_by(id=id, user_id=user_id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404

    data = request.get_json()
    try:
        validated = workout_schema.load(data, partial=True)
    except Exception as e:
        return jsonify({"error": "Invalid input", "messages": getattr(e, "messages", str(e))}), 400

    for key, value in validated.items():
        setattr(workout, key, value)

    db.session.commit()
    workout_date = workout.created_at.strftime("%Y-%m-%d")
    exercise_name = workout.exercise_name
    message = f"Workout ({workout_date}): {exercise_name} updated"

    return jsonify({"message": message}), 200


@workout_bp.delete("/<int:id>")
@jwt_required()
@csrf_protect
def delete_workout(id):
    """
    Delete a workout by ID for the logged-in user.
    """
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 400

    workout = Workout.query.filter_by(id=id, user_id=user_id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404

    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout deleted"}), 200


# -------------------------
# UI ROUTES
# -------------------------

@workout_bp.route("/ui", methods=["GET"])
def workouts_page():
    """
    Render the workouts list page for the logged-in user.
    Requires JWT cookie; otherwise redirects to login page.
    """
    try:
        verify_jwt_in_request(locations=['cookies'])
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        user_workouts = sorted(user.workouts, key=lambda x: x.created_at, reverse=True)
        return render_template("workouts.html", workouts=user_workouts, current_user=user)
    except Exception:
        return render_template("login.html", error="Please login first")


@workout_bp.route("/ui/create", methods=["GET"])
def create_workout_page():
    """
    Render the create workout page for the logged-in user.
    Requires JWT cookie; otherwise redirects to login page.
    """
    try:
        verify_jwt_in_request(locations=['cookies'])
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        return render_template("create_workout.html", current_user=user)
    except Exception:
        return render_template("login.html", error="Please login first")


# -------------------------
# API PROXIES
# -------------------------

@workout_bp.route("/api/search-exercises", methods=["GET"])
@jwt_required()
def proxy_search_exercises():
    """
    Proxy to search exercises from API Ninjas, with local fallback.
    """
    query = request.args.get("query", "").strip()
    muscle = request.args.get("muscle", "").strip()
    api_key = "ZkS5iFS/NKI7TC8m+KaqFA==cpScXc3ACH7s9TCj"

    local_fallback_exercises = [
        {"name": "Barbell Bench Press", "muscle": "chest", "difficulty": "intermediate"},
        {"name": "Dumbbell Flys", "muscle": "chest", "difficulty": "beginner"},
        {"name": "Pushups", "muscle": "chest", "difficulty": "beginner"},
        {"name": "Incline Bench Press", "muscle": "chest", "difficulty": "intermediate"},
        {"name": "Squat", "muscle": "legs", "difficulty": "intermediate"},
        {"name": "Leg Press", "muscle": "legs", "difficulty": "beginner"},
        {"name": "Lunges", "muscle": "legs", "difficulty": "beginner"},
        {"name": "Deadlift", "muscle": "back", "difficulty": "expert"},
        {"name": "Pullups", "muscle": "back", "difficulty": "intermediate"},
        {"name": "Lat Pulldown", "muscle": "back", "difficulty": "beginner"},
        {"name": "Dumbbell Rows", "muscle": "back", "difficulty": "intermediate"},
        {"name": "Plank", "muscle": "abs", "difficulty": "beginner"},
        {"name": "Crunches", "muscle": "abs", "difficulty": "beginner"},
        {"name": "Running", "muscle": "cardio", "difficulty": "beginner"},
        {"name": "Cycling", "muscle": "cardio", "difficulty": "beginner"},
        {"name": "Jump Rope", "muscle": "cardio", "difficulty": "intermediate"},
        {"name": "Bicep Curls", "muscle": "biceps", "difficulty": "beginner"},
        {"name": "Tricep Dips", "muscle": "triceps", "difficulty": "intermediate"}
    ]

    api_url = "https://api.api-ninjas.com/v1/exercises"
    params = {}
    if query:
        params["name"] = query
    if muscle:
        params["muscle"] = muscle

    if params:
        try:
            response = requests.get(api_url, headers={'X-Api-Key': api_key}, params=params)
            if response.status_code == 200:
                return jsonify(response.json())
            else:
                print(f"External API Failed (Using Fallback): {response.status_code} - {response.text}")
        except Exception as e:
            print(f"External API Exception (Using Fallback): {str(e)}")

    filtered_results = [
        ex for ex in local_fallback_exercises
        if (not muscle or muscle.lower() == ex["muscle"]) and (not query or query.lower() in ex["name"].lower())
    ]
    return jsonify(filtered_results)


@workout_bp.route("/api/generate-workout", methods=["POST"])
@jwt_required()
@csrf_protect
def proxy_generate_workout():
    """
    Proxy to generate AI workout via Ollama, with fallback to mock exercises.
    """
    data = request.get_json()
    user_prompt = data.get("prompt", "")

    system_prompt = (
        "You are a fitness trainer. Create a workout based on the user request. "
        "Return ONLY a JSON array of objects. Each object must have: "
        "'exercise_name', 'sets' (int), 'reps' (int), 'notes' (string). "
        "Do not include any markdown formatting or text outside the JSON."
    )

    payload = {
        "model": "goosedev/luna",
        "prompt": f"{system_prompt}\nUser Request: {user_prompt}",
        "stream": False
    }

    try:
        print(f"Connecting to Ollama with model: {payload['model']}...")
        base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        ollama_url = f"{base_url}/api/generate"

        response = requests.post(ollama_url, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            return jsonify({"response": result.get("response", "")})
        else:
            print(f"Ollama Error: {response.status_code} - {response.text}")
            raise Exception(f"Ollama Status {response.status_code}")

    except Exception as e:
        print(f"AI Generation Failed: {str(e)}")
        print("Falling back to simulated AI response for demo purposes.")

        mock_exercises = [
            {"exercise_name": "Pushups (AI Generated)", "sets": 3, "reps": 15, "notes": "Generated by Fallback Logic"},
            {"exercise_name": "Squats (AI Generated)", "sets": 4, "reps": 12, "notes": "Focus on depth"},
            {"exercise_name": "Plank (AI Generated)", "sets": 3, "reps": 60, "notes": "Keep core tight"},
            {"exercise_name": "Lunges (AI Generated)", "sets": 3, "reps": 10, "notes": "Per leg"}
        ]

        if "leg" in user_prompt.lower():
            selection = [mock_exercises[1], mock_exercises[3]]
        elif "chest" in user_prompt.lower() or "push" in user_prompt.lower():
            selection = [mock_exercises[0], mock_exercises[2]]
        else:
            selection = mock_exercises[:3]

        return jsonify({"response": json.dumps(selection)})


@workout_bp.route("/batch", methods=["POST"])
@jwt_required()
@csrf_protect
def create_batch_workouts():
    """
    Batch create workouts with automatic duration and calorie estimation.
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        data = request.get_json()

        created_items = []

        for item in data:
            # Extract duration
            try:
                duration = float(item.get("duration_minutes"))
            except (TypeError, ValueError):
                duration = 15.0

            # Calculate calories
            est_cals = float(item.get("calories_burned")) if item.get("calories_burned") else duration * 6.0

            workout = Workout(
                user_id=user.id,
                exercise_name=item.get("exercise_name"),
                sets=int(item.get("sets", 0)) if item.get("sets") else None,
                reps=int(item.get("reps", 0)) if item.get("reps") else None,
                weight_lbs=float(item.get("weight_lbs", 0)) if item.get("weight_lbs") else None,
                notes=item.get("notes", ""),
                duration_minutes=duration,
                calories_burned=est_cals
            )
            db.session.add(workout)
            created_items.append(workout)

        db.session.commit()
        return jsonify({"message": "Workouts saved successfully", "count": len(created_items)}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
