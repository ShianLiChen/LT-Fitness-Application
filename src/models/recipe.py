# src/models/recipe.py
from database import db
from datetime import datetime


# -------------------------
# Recipe Model
# -------------------------
class Recipe(db.Model):
    """
    Database model for storing recipes created by users.
    Includes title, ingredients, instructions, image URL, and nutrition data.
    """

    __tablename__ = "recipes"

    # -------------------------
    # Columns
    # -------------------------
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(150), nullable=False)
    ingredients = db.Column(db.Text, nullable=True)  # Stored as text (e.g., "2 eggs, 1 cup flour")
    instructions = db.Column(db.Text, nullable=True)  # Step-by-step instructions
    image_url = db.Column(db.String(500), nullable=True)  # URL to image (from API or placeholder)

    # Nutrition Data (Estimated)
    calories = db.Column(db.Integer, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fats = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # -------------------------
    # Relationships
    # -------------------------
    user = db.relationship("User", back_populates="recipes")

    # -------------------------
    # Utility Methods
    # -------------------------
    def to_dict(self):
        """
        Serialize Recipe object to a dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "ingredients": self.ingredients,
            "instructions": self.instructions,
            "image_url": self.image_url,
            "calories": self.calories,
            "protein": self.protein,
            "carbs": self.carbs,
            "fats": self.fats,
            "created_at": self.created_at.isoformat(),
        }
