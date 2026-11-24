"""
Unit and Integration Test Suite for Community Recipe Sharing Platform.
Tests all REST API endpoints, SQLite transactional integrity, validation rules,
ingredient image mapping, and like/unlike atomic counters.
"""

import os
import tempfile
import unittest
import sqlite3
from app import app, resolve_ingredient_image
from db import init_db
from seed import seed


class TestCommunityRecipePlatform(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.environ["DATABASE_PATH"] = self.db_path
        app.config["TESTING"] = True
        app.config["DATABASE_PATH"] = self.db_path
        self.client = app.test_client()

        # Initialize schema and seed data into isolated test database
        init_db(self.db_path)
        seed(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_home_page_renders_cleanly(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Community Recipe", res.data)
        self.assertIn(b"Unlock Your", res.data)
        self.assertIn(b"Inner Chef", res.data)

    def test_get_recipes_api_with_images(self):
        res = self.client.get("/api/recipes")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 20)
        first = data[0]
        self.assertIn("title", first)
        self.assertIn("category", first)
        self.assertIn("image", first)
        self.assertTrue(first["image"].startswith("/static/images/recipes/"))

    def test_search_and_category_filter(self):
        # Search by ingredient "avocado"
        res = self.client.get("/api/recipes?q=avocado")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(len(data), 1)
        self.assertTrue(any("Avocado" in r["title"] for r in data))

        # Search with category "Breakfast"
        res = self.client.get("/api/recipes?category=Breakfast")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        for r in data:
            self.assertEqual(r["category"], "Breakfast")

    def test_get_single_recipe_detail_with_ingredient_images(self):
        res = self.client.get("/api/recipes/1")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("ingredients", data)
        self.assertIn("steps", data)
        self.assertGreater(len(data["ingredients"]), 0)
        self.assertIn("image", data["ingredients"][0])
        self.assertTrue(data["ingredients"][0]["image"].startswith("/static/images/ingredients/"))

    def test_get_unknown_recipe_returns_404(self):
        res = self.client.get("/api/recipes/99999")
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertIn("error", data)

    def test_create_recipe_validation_errors(self):
        # Missing title
        res = self.client.post("/api/recipes", json={
            "cuisine": "Italian",
            "category": "Lunch",
            "prep_time": 20,
            "difficulty": "Easy",
            "ingredients": ["Pasta"],
            "steps": ["Boil water"]
        })
        self.assertEqual(res.status_code, 400)

        # Invalid category
        res = self.client.post("/api/recipes", json={
            "title": "Invalid Cat",
            "cuisine": "Italian",
            "category": "Dinner",  # Not allowed
            "prep_time": 20,
            "difficulty": "Easy",
            "ingredients": ["Pasta"],
            "steps": ["Boil water"]
        })
        self.assertEqual(res.status_code, 400)

        # Invalid prep time
        res = self.client.post("/api/recipes", json={
            "title": "Bad Time",
            "cuisine": "Italian",
            "category": "Lunch",
            "prep_time": 0,  # Must be >= 1
            "difficulty": "Easy",
            "ingredients": ["Pasta"],
            "steps": ["Boil water"]
        })
        self.assertEqual(res.status_code, 400)

        # Empty ingredients
        res = self.client.post("/api/recipes", json={
            "title": "No ingredients",
            "cuisine": "Italian",
            "category": "Lunch",
            "prep_time": 15,
            "difficulty": "Easy",
            "ingredients": ["   "],
            "steps": ["Boil water"]
        })
        self.assertEqual(res.status_code, 400)

    def test_create_recipe_success_and_transaction(self):
        new_recipe = {
            "title": "Greek Summer Watermelon Salad",
            "cuisine": "Greek",
            "category": "Lunch",
            "prep_time": 15,
            "difficulty": "Easy",
            "ingredients": [
                "4 cups fresh watermelon cubes",
                "1 cup crumbled Greek feta cheese",
                "Fresh mint leaves & balsamic drizzle"
            ],
            "steps": [
                "Cut cold watermelon into bite-sized cubes.",
                "Toss with crumbled feta cheese and torn fresh mint leaves.",
                "Drizzle lightly with extra virgin olive oil and balsamic glaze."
            ]
        }
        res = self.client.post("/api/recipes", json=new_recipe)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        recipe_id = data["id"]
        self.assertIsInstance(recipe_id, int)

        # Verify retrieval via detail endpoint
        res = self.client.get(f"/api/recipes/{recipe_id}")
        self.assertEqual(res.status_code, 200)
        rec = res.get_json()
        self.assertEqual(rec["title"], new_recipe["title"])
        self.assertEqual(len(rec["ingredients"]), 3)
        self.assertEqual(len(rec["steps"]), 3)

    def test_like_and_unlike_atomic_counter(self):
        # Initial likes
        res = self.client.get("/api/recipes/1")
        initial_likes = res.get_json()["likes"]

        # Like recipe
        res = self.client.post("/api/recipes/1/like", json={"action": "like"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["likes"], initial_likes + 1)

        # Unlike recipe
        res = self.client.post("/api/recipes/1/like", json={"action": "unlike"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["likes"], initial_likes)

    def test_like_counter_never_below_zero(self):
        # Create zero-like recipe
        db = sqlite3.connect(self.db_path)
        cur = db.execute(
            "INSERT INTO recipes (title, cuisine, category, prep_time, difficulty, likes) VALUES (?, ?, ?, ?, ?, ?)",
            ("Zero Like Recipe", "Test", "Breakfast", 10, "Easy", 0)
        )
        zero_id = cur.lastrowid
        db.commit()
        db.close()

        # Attempt to unlike below zero
        res = self.client.post(f"/api/recipes/{zero_id}/like", json={"action": "unlike"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["likes"], 0)

    def test_ingredient_image_keyword_resolver(self):
        self.assertIn("avocado.jpg", resolve_ingredient_image("Fresh ripe avocado"))
        self.assertIn("cheese.jpg", resolve_ingredient_image("Crumbled Greek feta cheese"))
        self.assertIn("bread.jpg", resolve_ingredient_image("Toasted sourdough bread"))
        self.assertIn("default_food.jpg", resolve_ingredient_image("Unicorn rainbow dust"))


if __name__ == "__main__":
    unittest.main()
