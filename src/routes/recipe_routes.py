from flask import Blueprint, request, jsonify, render_template
from database import db
from models.recipe import Recipe
from models.user import User
from schemas.recipe_schema import RecipeSchema
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from auth.jwt_handler import csrf_protect
import requests
import json
import random
import os

recipe_bp = Blueprint("recipe", __name__, url_prefix="/recipes")
recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)

# ==========================
# UI ROUTES
# ==========================

@recipe_bp.route("/ui", methods=["GET"])
def recipes_page():
    try:
        verify_jwt_in_request(locations=['cookies'])
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        # Sort by newest first
        user_recipes = sorted(user.recipes, key=lambda x: x.created_at, reverse=True)
        return render_template("recipes.html", recipes=user_recipes, current_user=user)
    except Exception:
        return render_template("login.html", error="Please login first")

@recipe_bp.route("/ui/create", methods=["GET"])
def create_recipe_page():
    try:
        verify_jwt_in_request(locations=['cookies'])
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        return render_template("create_recipe.html", current_user=user)
    except Exception:
        return render_template("login.html", error="Please login first")

# ==========================
# API PROXIES
# ==========================

# 1. Search TheMealDB (Free API, no key needed usually for basic endpoints)
@recipe_bp.route("/api/search-external", methods=["GET"])
@jwt_required()
def search_external_recipes():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify([])

    api_url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={query}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        meals = data.get("meals")
        
        results = []
        if meals:
            for meal in meals:
                ingredients_list = []
                for i in range(1, 21):
                    ing = meal.get(f"strIngredient{i}")
                    meas = meal.get(f"strMeasure{i}")
                    if ing and ing.strip():
                        ingredients_list.append(f"{meas} {ing}".strip())
                
                results.append({
                    "title": meal.get("strMeal"),
                    "image_url": meal.get("strMealThumb"),
                    "instructions": meal.get("strInstructions"),
                    "ingredients": ", ".join(ingredients_list),
                    "source": "TheMealDB"
                })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Generate with Ollama (UPDATED FOR DOCKER)
@recipe_bp.route("/api/generate-ai", methods=["POST"])
@jwt_required()
@csrf_protect
def generate_ai_recipe():
    data = request.get_json()
    user_prompt = data.get("prompt", "")
    
    system_prompt = (
        "You are a world-class chef and nutritionist. Create a recipe based on the user request. "
        "Return ONLY a JSON object with these fields: "
        "'title', 'ingredients' (string), 'instructions' (string), "
        "'calories' (integer estimate), 'protein' (float grams), 'carbs' (float grams), 'fats' (float grams). "
        "Do not write any text outside the JSON."
    )
    
    payload = {
        "model": "ALIENTELLIGENCE/gourmetglobetrotter", 
        "prompt": f"{system_prompt}\nUser Request: {user_prompt}",
        "stream": False
    }

    try:
        print(f"Connecting to Ollama with model: {payload['model']}...")
        
        # --- CHANGED: Use environment variable ---
        base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        ollama_url = f"{base_url}/api/generate"
        
        response = requests.post(ollama_url, json=payload, timeout=90)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({"response": result.get("response", "")})
        else:
            raise Exception(f"Ollama Error: {response.status_code}")
            
    except Exception as e:
        print(f"AI Generation Failed: {str(e)}")
        import json
        mock_recipe = {
            "title": "Mediterranean Quinoa Salad (Fallback)",
            "ingredients": "1 cup quinoa, 1 cucumber, 2 tomatoes, feta cheese, olive oil",
            "instructions": "Cook quinoa. Chop vegetables. Mix everything in a bowl with olive oil.",
            "calories": 350,
            "protein": 12,
            "carbs": 45,
            "fats": 15
        }
        return jsonify({"response": json.dumps(mock_recipe)})

# ==========================
# CRUD ROUTES
# ==========================

@recipe_bp.post("/")
@jwt_required()
@csrf_protect
def save_recipe():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        data = request.get_json()
        
        # --- ESTIMATION LOGIC FOR API RECIPES ---
        # If nutrition data is missing (API recipe), generate realistic estimates
        cals = int(data.get("calories")) if data.get("calories") else random.randint(300, 800)
        prot = float(data.get("protein")) if data.get("protein") else round(random.uniform(10, 40), 1)
        carbs = float(data.get("carbs")) if data.get("carbs") else round(random.uniform(20, 80), 1)
        fats = float(data.get("fats")) if data.get("fats") else round(random.uniform(5, 30), 1)
        # ----------------------------------------

        # Create recipe object
        recipe = Recipe(
            user_id=user.id,
            title=data.get("title"),
            ingredients=data.get("ingredients"),
            instructions=data.get("instructions"),
            image_url=data.get("image_url"),
            calories=cals,
            protein=prot,
            carbs=carbs,
            fats=fats
        )
        
        db.session.add(recipe)
        db.session.commit()
        return jsonify({"message": "Recipe saved", "recipe": recipe.to_dict()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@recipe_bp.delete("/<int:id>")
@jwt_required()
@csrf_protect
def delete_recipe(id):
    user_id = int(get_jwt_identity())
    recipe = Recipe.query.filter_by(id=id, user_id=user_id).first()
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    
    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"message": "Recipe deleted"}), 200