# src/models/user.py
from database import db
from datetime import datetime


# -------------------------
# User Model
# -------------------------
class User(db.Model):
    """
    Database model for application users.
    Stores username, email, hashed password, role, and creation timestamp.
    """

    __tablename__ = "users"

    # -------------------------
    # Columns
    # -------------------------
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -------------------------
    # Relationships
    # -------------------------
    workouts = db.relationship(
        "Workout", back_populates="user", cascade="all, delete-orphan"
    )
    recipes = db.relationship(
        "Recipe", back_populates="user", cascade="all, delete-orphan"
    )
    reset_tokens = db.relationship(
        "PasswordResetToken", back_populates="user", cascade="all, delete-orphan"
    )

    # -------------------------
    # Utility Methods
    # -------------------------
    def to_dict(self):
        """
        Serialize User object to a dictionary.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }
