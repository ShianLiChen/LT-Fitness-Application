# src/models/workout.py
from database import db
from datetime import datetime


# -------------------------
# Workout Model
# -------------------------
class Workout(db.Model):
    """
    Database model for tracking user workouts.
    Stores exercise details, duration, sets, reps, weight, calories, and timestamps.
    """

    __tablename__ = "workouts"

    # -------------------------
    # Columns
    # -------------------------
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Float, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.Integer, nullable=True)
    weight_lbs = db.Column(db.Float, nullable=True)
    machine = db.Column(db.String(100), nullable=True)
    calories_burned = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -------------------------
    # Relationships
    # -------------------------
    user = db.relationship("User", back_populates="workouts")

    # -------------------------
    # Utility Methods
    # -------------------------
    def to_dict(self):
        """
        Serialize Workout object to a dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "exercise_name": self.exercise_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_minutes": self.duration_minutes,
            "sets": self.sets,
            "reps": self.reps,
            "weight_lbs": self.weight_lbs,
            "machine": self.machine,
            "calories_burned": self.calories_burned,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }
