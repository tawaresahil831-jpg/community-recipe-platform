#!/usr/bin/env python3
"""
Community Recipe Sharing Platform
Flask Backend Application
"""

import os
import sqlite3
from typing import Optional, List, Dict, Any, Tuple
from dotenv import load_dotenv
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    abort,
    g,
    Response,
)

load_dotenv()

from db import get_db, close_db, init_db, get_db_path

app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-dev-recipe-key")
app.config["DATABASE_PATH"] = os.getenv("DATABASE_PATH", "recipes.db")

ALLOWED_CATEGORIES = ("Breakfast", "Lunch", "Dessert", "Vegan")
ALLOWED_DIFFICULTIES = ("Easy", "Medium", "Hard")

app.teardown_appcontext(close_db)


@app.template_filter("format_date")
def format_date_filter(val: Any) -> str:
    """Format datetime or string timestamp to YYYY-MM-DD."""
    if not val:
        return "Recently"
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    return str(val)[:10]


INGREDIENT_IMAGE_MAPPINGS = [
    (("avocado",), "avocado.jpg"),
    (("egg", "yolk"), "egg.jpg"),
    (("bread", "toast", "ladyfinger", "sourdough"), "bread.jpg"),
    (("olive oil", "oil", "vinegar"), "olive_oil.jpg"),
    (("blueberry", "blueberries", "berry", "berries"), "blueberries.jpg"),
    (("flour", "baking powder", "baking soda", "cornstarch"), "flour.jpg"),
    (("butter", "buttermilk", "cream", "milk"), "butter.jpg"),
    (("syrup", "sugar"), "syrup.jpg"),
    (("quinoa", "rice"), "quinoa.jpg"),
    (("tomato", "puree"), "tomatoes.jpg"),
    (("cucumber",), "cucumber.jpg"),
    (("olive", "olives"), "olives.jpg"),
    (("cheese", "mozzarella", "feta", "parmesan", "mascarpone"), "cheese.jpg"),
    (("chickpea", "chickpeas", "bean", "beans"), "chickpeas.jpg"),
    (("garlic", "onion", "ginger"), "garlic.jpg"),
    (("basil", "spinach", "herb", "parsley", "nori", "cilantro", "oregano"), "herbs.jpg"),
    (("chicken", "pork", "steak", "meat", "chashu"), "chicken.jpg"),
    (("pasta", "fettuccine", "noodle", "noodles", "spaghetti", "penne"), "pasta.jpg"),
    (("chocolate", "cocoa"), "chocolate.jpg"),
    (("coffee", "espresso", "liqueur"), "coffee.jpg"),
    (("coconut",), "coconut.jpg"),
    (("bell pepper", "pepper"), "bell_pepper.jpg"),
    (("lemon", "lime"), "lemon.jpg"),
    (("tofu",), "tofu.jpg"),
    (("salt", "spice", "spices", "seasoning", "flakes"), "spices.jpg"),
]


def resolve_ingredient_image(name: str) -> str:
    """Return URL for a delicious ingredient image based on keywords."""
    name_lower = name.lower()
    for keywords, filename in INGREDIENT_IMAGE_MAPPINGS:
        if any(kw in name_lower for kw in keywords):
            return f"/static/images/ingredients/{filename}"
    return "/static/images/ingredients/default_food.jpg"


@app.template_filter("ingredient_image")
def ingredient_image_filter(val: Any) -> str:
    """Jinja filter to get ingredient image URL."""
    return resolve_ingredient_image(str(val))


# -----------------------------------------------------------------------------
# Web Page Views
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """Home page: Explore feed with category chips, live search, and recipe grid."""
    db = get_db()
    recipes = db.execute(
        """
        SELECT r.id, r.title, r.cuisine, r.category, r.prep_time, r.difficulty, r.likes, r.created_at,
               (SELECT name FROM ingredients WHERE recipe_id = r.id ORDER BY position ASC LIMIT 1) AS primary_ingredient
        FROM recipes r
        ORDER BY r.created_at DESC, r.id DESC
        """
    ).fetchall()
    return render_template("index.html", recipes=recipes, categories=ALLOWED_CATEGORIES)


@app.route("/create")
def create_recipe_page():
    """Recipe creation form with dynamic ingredient & step builders."""
    return render_template(
        "create.html",
        categories=ALLOWED_CATEGORIES,
        difficulties=ALLOWED_DIFFICULTIES,
    )


@app.route("/recipe/<int:recipe_id>")
def recipe_page(recipe_id: int):
    """Recipe detail page with interactive checklist, numbered steps, and like button."""
    db = get_db()
    recipe = db.execute(
        """
        SELECT id, title, cuisine, category, prep_time, difficulty, likes, created_at
        FROM recipes WHERE id = ?
        """,
        (recipe_id,),
    ).fetchone()

    if not recipe:
        abort(404)

    ingredients = db.execute(
        "SELECT id, name, position FROM ingredients WHERE recipe_id = ? ORDER BY position ASC, id ASC",
        (recipe_id,),
    ).fetchall()

    steps = db.execute(
        "SELECT id, instruction, position FROM steps WHERE recipe_id = ? ORDER BY position ASC, id ASC",
        (recipe_id,),
    ).fetchall()

    return render_template(
        "recipe.html",
        recipe=recipe,
        ingredients=ingredients,
        steps=steps,
    )


# -----------------------------------------------------------------------------
# REST API Endpoints (/api)
# -----------------------------------------------------------------------------

@app.route("/api/recipes", methods=["GET"])
def api_get_recipes():
    """
    GET /api/recipes?category=&q=
    Returns a list of recipes filtered by optional category and search query 'q'.
    'q' searches across title, cuisine, and ingredient names (case-insensitive).
    """
    category = request.args.get("category", "").strip()
    q = request.args.get("q", "").strip()

    db = get_db()
    conditions = []
    params = []

    if category and category.lower() != "all":
        # Match case-insensitively with allowed categories
        matched_cat = next((c for c in ALLOWED_CATEGORIES if c.lower() == category.lower()), None)
        if matched_cat:
            conditions.append("r.category = ?")
            params.append(matched_cat)

    if q:
        search_pattern = f"%{q}%"
        conditions.append(
            """
            (
                r.title LIKE ?
                OR r.cuisine LIKE ?
                OR EXISTS (
                    SELECT 1 FROM ingredients i
                    WHERE i.recipe_id = r.id AND i.name LIKE ?
                )
            )
            """
        )
        params.extend([search_pattern, search_pattern, search_pattern])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT r.id, r.title, r.cuisine, r.category, r.prep_time, r.difficulty, r.likes, r.created_at,
               (SELECT name FROM ingredients WHERE recipe_id = r.id ORDER BY position ASC LIMIT 1) AS primary_ingredient
        FROM recipes r
        {where_clause}
        ORDER BY r.created_at DESC, r.id DESC
    """

    rows = db.execute(query, params).fetchall()

    result = []
    for r in rows:
        created_str = (
            r["created_at"].isoformat()
            if hasattr(r["created_at"], "isoformat")
            else str(r["created_at"])
        )
        primary_ing = r["primary_ingredient"] or r["title"]
        result.append({
            "id": r["id"],
            "title": r["title"],
            "cuisine": r["cuisine"],
            "category": r["category"],
            "prep_time": r["prep_time"],
            "difficulty": r["difficulty"],
            "likes": r["likes"],
            "created_at": created_str,
            "image": resolve_ingredient_image(primary_ing),
        })

    return jsonify(result), 200


@app.route("/api/recipes/<int:recipe_id>", methods=["GET"])
def api_get_recipe(recipe_id: int):
    """GET /api/recipes/<id> -> Full recipe details with ordered ingredients and steps."""
    db = get_db()
    recipe = db.execute(
        """
        SELECT id, title, cuisine, category, prep_time, difficulty, likes, created_at
        FROM recipes WHERE id = ?
        """,
        (recipe_id,),
    ).fetchone()

    if not recipe:
        return jsonify({"error": "Recipe not found."}), 404

    ingredients_rows = db.execute(
        "SELECT id, name, position FROM ingredients WHERE recipe_id = ? ORDER BY position ASC, id ASC",
        (recipe_id,),
    ).fetchall()

    steps_rows = db.execute(
        "SELECT id, instruction, position FROM steps WHERE recipe_id = ? ORDER BY position ASC, id ASC",
        (recipe_id,),
    ).fetchall()

    created_str = (
        recipe["created_at"].isoformat()
        if hasattr(recipe["created_at"], "isoformat")
        else str(recipe["created_at"])
    )

    return jsonify({
        "id": recipe["id"],
        "title": recipe["title"],
        "cuisine": recipe["cuisine"],
        "category": recipe["category"],
        "prep_time": recipe["prep_time"],
        "difficulty": recipe["difficulty"],
        "likes": recipe["likes"],
        "created_at": created_str,
        "ingredients": [
            {
                "id": ing["id"],
                "name": ing["name"],
                "position": ing["position"],
                "image": resolve_ingredient_image(ing["name"]),
            }
            for ing in ingredients_rows
        ],
        "steps": [
            {"id": st["id"], "instruction": st["instruction"], "position": st["position"]}
            for st in steps_rows
        ],
    }), 200


@app.route("/api/recipes", methods=["POST"])
def api_create_recipe():
    """
    POST /api/recipes
    Body: {
        "title": str,
        "cuisine": str,
        "category": str,
        "prep_time": int,
        "difficulty": str,
        "ingredients": [str, ...],
        "steps": [str, ...]
    }
    Validation:
      - title: required non-empty string (max 120 chars)
      - cuisine: required non-empty string (max 100 chars)
      - category: one of ('Breakfast', 'Lunch', 'Dessert', 'Vegan')
      - prep_time: integer 1 to 1440
      - difficulty: one of ('Easy', 'Medium', 'Hard')
      - ingredients: at least 1 item, each non-empty string (max 200 chars)
      - steps: at least 1 item, each non-empty string (max 200 chars)
    Returns: 201 with recipe ID
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body. Expected an object."}), 400

    # 1. Validate title
    raw_title = data.get("title")
    if not isinstance(raw_title, str) or not raw_title.strip():
        return jsonify({"error": "Recipe title is required and cannot be empty."}), 400
    title = raw_title.strip()
    if len(title) > 120:
        return jsonify({"error": "Recipe title must be at most 120 characters."}), 400

    # 2. Validate cuisine
    raw_cuisine = data.get("cuisine")
    if not isinstance(raw_cuisine, str) or not raw_cuisine.strip():
        return jsonify({"error": "Cuisine type is required and cannot be empty."}), 400
    cuisine = raw_cuisine.strip()
    if len(cuisine) > 100:
        return jsonify({"error": "Cuisine must be at most 100 characters."}), 400

    # 3. Validate category
    category = data.get("category")
    if category not in ALLOWED_CATEGORIES:
        return jsonify({
            "error": f"Invalid category '{category}'. Must be one of: {', '.join(ALLOWED_CATEGORIES)}."
        }), 400

    # 4. Validate prep_time
    prep_time = data.get("prep_time")
    if not isinstance(prep_time, int) or prep_time < 1 or prep_time > 1440:
        return jsonify({"error": "Prep time must be an integer between 1 and 1440 minutes."}), 400

    # 5. Validate difficulty
    difficulty = data.get("difficulty")
    if difficulty not in ALLOWED_DIFFICULTIES:
        return jsonify({
            "error": f"Invalid difficulty '{difficulty}'. Must be one of: {', '.join(ALLOWED_DIFFICULTIES)}."
        }), 400

    # 6. Validate ingredients
    raw_ingredients = data.get("ingredients")
    if not isinstance(raw_ingredients, list) or len(raw_ingredients) < 1:
        return jsonify({"error": "At least one ingredient is required."}), 400

    cleaned_ingredients = []
    for idx, ing in enumerate(raw_ingredients):
        if not isinstance(ing, str) or not ing.strip():
            return jsonify({"error": f"Ingredient at position {idx + 1} cannot be blank."}), 400
        cleaned_ing = ing.strip()
        if len(cleaned_ing) > 200:
            return jsonify({
                "error": f"Ingredient '{cleaned_ing[:20]}...' exceeds 200 characters limit."
            }), 400
        cleaned_ingredients.append(cleaned_ing)

    # 7. Validate steps
    raw_steps = data.get("steps")
    if not isinstance(raw_steps, list) or len(raw_steps) < 1:
        return jsonify({"error": "At least one preparation step is required."}), 400

    cleaned_steps = []
    for idx, step in enumerate(raw_steps):
        if not isinstance(step, str) or not step.strip():
            return jsonify({"error": f"Step at position {idx + 1} cannot be blank."}), 400
        cleaned_step = step.strip()
        if len(cleaned_step) > 200:
            return jsonify({
                "error": f"Step '{cleaned_step[:20]}...' exceeds 200 characters limit."
            }), 400
        cleaned_steps.append(cleaned_step)

    # Wrap insert in a single transaction
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO recipes (title, cuisine, category, prep_time, difficulty, likes)
            VALUES (?, ?, ?, ?, ?, 0)
            """,
            (title, cuisine, category, prep_time, difficulty),
        )
        recipe_id = cursor.lastrowid

        for pos, ing_text in enumerate(cleaned_ingredients):
            cursor.execute(
                "INSERT INTO ingredients (recipe_id, name, position) VALUES (?, ?, ?)",
                (recipe_id, ing_text, pos),
            )

        for pos, step_text in enumerate(cleaned_steps):
            cursor.execute(
                "INSERT INTO steps (recipe_id, instruction, position) VALUES (?, ?, ?)",
                (recipe_id, step_text, pos),
            )

        db.commit()
    except Exception as exc:
        db.rollback()
        return jsonify({"error": f"Database transaction failed: {str(exc)}"}), 500

    return jsonify({
        "id": recipe_id,
        "title": title,
        "message": "Recipe created successfully.",
    }), 201


@app.route("/api/recipes/<int:recipe_id>/like", methods=["POST"])
def api_like_recipe(recipe_id: int):
    """
    POST /api/recipes/<id>/like
    Body: { "action": "like" | "unlike" }
    Atomically updates likes counter. Ensures likes never drop below 0.
    Returns: updated like count
    """
    db = get_db()
    recipe = db.execute("SELECT id, likes FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    if not recipe:
        return jsonify({"error": "Recipe not found."}), 404

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid JSON body. Expected { 'action': 'like' | 'unlike' }."}), 400

    action = data.get("action")
    if action not in ("like", "unlike"):
        return jsonify({"error": "Invalid action. Must be 'like' or 'unlike'."}), 400

    if action == "like":
        db.execute(
            "UPDATE recipes SET likes = likes + 1 WHERE id = ?",
            (recipe_id,),
        )
    else:
        # Decrement, guaranteed never below 0
        db.execute(
            "UPDATE recipes SET likes = MAX(0, likes - 1) WHERE id = ?",
            (recipe_id,),
        )
    db.commit()

    updated = db.execute("SELECT likes FROM recipes WHERE id = ?", (recipe_id,)).fetchone()
    new_likes = updated["likes"] if updated else 0

    return jsonify({
        "id": recipe_id,
        "likes": new_likes,
        "action": action,
        "message": f"Recipe successfully {action}d.",
    }), 200


@app.errorhandler(404)
def not_found_handler(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Resource not found."}), 404
    return render_template("index.html", error_message="The requested recipe or page was not found."), 404


@app.errorhandler(500)
def server_error_handler(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error."}), 500
    return render_template("index.html", error_message="An unexpected server error occurred."), 500


if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
