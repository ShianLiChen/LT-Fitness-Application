from database import db
from datetime import datetime

class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    title = db.Column(db.String(150), nullable=False)
    ingredients = db.Column(db.Text, nullable=True)   # Stored as text (e.g., "2 eggs, 1 cup flour")
    instructions = db.Column(db.Text, nullable=True)  # Step-by-step instructions
    image_url = db.Column(db.String(500), nullable=True) # URL to image (from API or placeholder)
    
    # Nutrition Data (Estimated)
    calories = db.Column(db.Integer, nullable=True)
    protein = db.Column(db.Float, nullable=True)
    carbs = db.Column(db.Float, nullable=True)
    fats = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", back_populates="recipes")

    def to_dict(self):
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
            "created_at": self.created_at.isoformat()
        }