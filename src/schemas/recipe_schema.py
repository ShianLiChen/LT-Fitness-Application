# src/schemas/recipe_schema.py
from marshmallow import Schema, fields, validates, ValidationError


# -------------------------
# Recipe Schema
# -------------------------
class RecipeSchema(Schema):
    """
    Schema for validating and serializing Recipe objects.
    """

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    ingredients = fields.Str(load_default="")
    instructions = fields.Str(load_default="")
    image_url = fields.Str(allow_none=True)

    # Nutrition
    calories = fields.Int(allow_none=True)
    protein = fields.Float(allow_none=True)
    carbs = fields.Float(allow_none=True)
    fats = fields.Float(allow_none=True)

    created_at = fields.DateTime(dump_only=True)

    # -------------------------
    # Validations
    # -------------------------
    @validates("title")
    def validate_title(self, value, **kwargs):
        """
        Ensure the title is not empty or only whitespace.
        """
        if not value or not value.strip():
            raise ValidationError("Title cannot be empty")
