# src/schemas/workout_schema.py
from marshmallow import Schema, fields, validate


# -------------------------
# Workout Schema
# -------------------------
class WorkoutSchema(Schema):
    """
    Schema for validating and serializing Workout objects.
    """

    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    exercise_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime()
    duration_minutes = fields.Float()
    sets = fields.Int()
    reps = fields.Int()
    weight_lbs = fields.Float()
    machine = fields.Str()
    calories_burned = fields.Float()
    notes = fields.Str()
    created_at = fields.DateTime(dump_only=True)
