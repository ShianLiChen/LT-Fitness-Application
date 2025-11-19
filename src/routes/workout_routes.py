from flask import Blueprint, request, jsonify, g, render_template
from database import db
from models.workout import Workout
from schemas.workout_schema import WorkoutSchema
from auth.jwt_handler import jwt_required
from datetime import datetime, timedelta

workout_bp = Blueprint("workout", __name__, url_prefix="/workouts")
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

# --------------------
# Create a workout
# --------------------
@workout_bp.post("/")
@jwt_required
def create_workout():
    data = request.get_json()
    try:
        validated = workout_schema.load(data)
    except Exception as e:
        return jsonify({"error": "Invalid input", "messages": e.messages}), 400
    
    duration_calc = 0.0
    try:
        duration_calc = validated.get("end_time") - validated.get("start_time", datetime.utcnow())
        duration_calc = duration_calc.total_seconds()
        duration_calc = float(duration_calc/60)
    except Exception as e:
        return jsonify({"error": "Invalid calculation", "messages": e.messages}), 400

    workout = Workout(
        user_id=g.current_user.id,
        exercise_name=validated["exercise_name"],
        start_time=validated.get("start_time", datetime.utcnow()),
        end_time=validated.get("end_time"),
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
@jwt_required
def get_workouts():
    user = g.current_user
    return jsonify({"workouts": workouts_schema.dump(user.workouts)}), 200

# --------------------
# Get single workout by id
# --------------------
@workout_bp.get("/<int:id>")
@jwt_required
def get_workout(id):
    workout = Workout.query.filter_by(id=id, user_id=g.current_user.id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404
    return jsonify({"workout": workout_schema.dump(workout)}), 200

# --------------------
# Update a workout
# --------------------
@workout_bp.put("/<int:id>")
@jwt_required
def update_workout(id):
    workout = Workout.query.filter_by(id=id, user_id=g.current_user.id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404

    data = request.get_json()
    try:
        validated = workout_schema.load(data, partial=True)  # partial allows updating some fields
    except Exception as e:
        return jsonify({"error": "Invalid input", "messages": e.messages}), 400

    for key, value in validated.items():
        setattr(workout, key, value)

    db.session.commit()
    return jsonify({"message": "Workout updated", "workout": workout_schema.dump(workout)}), 200

# --------------------
# Delete a workout
# --------------------
@workout_bp.delete("/<int:id>")
@jwt_required
def delete_workout(id):
    workout = Workout.query.filter_by(id=id, user_id=g.current_user.id).first()
    if not workout:
        return jsonify({"error": "Workout not found"}), 404

    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout deleted"}), 200
