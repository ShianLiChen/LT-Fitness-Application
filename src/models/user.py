from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50), default="user")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # inside User class
    workouts = db.relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    recipes = db.relationship("Recipe", back_populates="user", cascade="all, delete-orphan")


    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }
    