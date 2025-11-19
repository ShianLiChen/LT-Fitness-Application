from marshmallow import Schema, fields

class RecipeSchema(Schema):
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