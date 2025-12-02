# src/models/password_reset_token.py
from database import db


# -------------------------
# Password Reset Token Model
# -------------------------
class PasswordResetToken(db.Model):
    """
    Database model for storing password reset tokens.
    Each token is linked to a user and has an expiration date.
    """

    __tablename__ = "password_reset_tokens"

    # -------------------------
    # Columns
    # -------------------------
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)

    # -------------------------
    # Relationships
    # -------------------------
    user = db.relationship("User", back_populates="reset_tokens")
