# workout_routes.py
from flask import Blueprint, request, jsonify, abort
from database import db
from models.workout import Workout
from models.user import User
from schemas.workout_schema import WorkoutSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

workout_bp = Blueprint("workout", __name__, url_prefix="/workouts")
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)


# --------------------
# Create a workout
# --------------------
@workout_bp.post("/")
@jwt_required()
def create_workout():
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
    duration_calc = None
    if start_time and end_time:
        duration_calc = (end_time - start_time).total_seconds() / 60

    workout = Workout(
        user_id=user.id,
        exercise_name=validated["exercise_name"],
        start_time=start_time,
        end_time=end_time,
        duration_minutes=validated.get("duration_minutes", duration_calc),
        sets=validated.get("sets"),
        reps=validated.get("reps"),
        weight_lbs=validated.get("weight_lbs"),
        machine=validated.get("machine"),
        calories_burned=validated.get("calories_burned"),
        notes=validated.get("notes")
    )

    db.session.add(workout)
    db.session.commit()
    return jsonify({"message": "Workout created", "workout": workout.to_dict()}), 201


# --------------------
# Get all workouts for the logged-in user
# --------------------
@workout_bp.get("/")
@jwt_required()
def get_workouts():
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"workouts": workouts_schema.dump(user.workouts)}), 200


# --------------------
# Get single workout by id
# --------------------
@workout_bp.get("/<int:id>")
@jwt_required()
def get_workout(id):
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity"}), 400

    workout = Workout.query.filter_by(id=id, user_id=user_id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404

    return jsonify({"workout": workout_schema.dump(workout)}), 200


# --------------------
# Update a workout
# --------------------
@workout_bp.put("/<int:id>")
@jwt_required()
def update_workout(id):
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
    return jsonify({"message": "Workout updated", "workout": workout_schema.dump(workout)}), 200


# --------------------
# Delete a workout
# --------------------
@workout_bp.delete("/<int:id>")
@jwt_required()
def delete_workout(id):
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
