#!/usr/bin/env python3
"""
Seed script for Community Recipe Sharing Platform.
Inserts at least 8 authentic sample recipes across Breakfast, Lunch, Dessert, and Vegan.
Safe to run multiple times (idempotent).
"""

import os
import sqlite3
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from db import init_db, get_db_path

SAMPLE_RECIPES = [
    {
        "title": "Avocado Toast with Poached Egg",
        "cuisine": "American",
        "category": "Breakfast",
        "prep_time": 15,
        "difficulty": "Easy",
        "likes": 28,
        "ingredients": [
            "2 thick slices sourdough bread",
            "1 ripe Hass avocado",
            "2 fresh large eggs",
            "1 tsp white vinegar (for poaching)",
            "1/4 tsp red pepper flakes",
            "1 tbsp extra virgin olive oil",
            "Flaky sea salt and freshly ground black pepper",
        ],
        "steps": [
            "Bring a pot of water to a gentle simmer with white vinegar; create a whirlpool and gently slip in the cracked egg to poach for 3 minutes.",
            "Toast sourdough slices until golden and crisp.",
            "In a bowl, coarsely mash the avocado with olive oil, sea salt, and black pepper.",
            "Spread mashed avocado evenly across the warm toasted sourdough.",
            "Top each slice with a drained poached egg, sprinkle with red pepper flakes and flaky sea salt, and serve immediately.",
        ],
    },
    {
        "title": "Fluffy Blueberry Buttermilk Pancakes",
        "cuisine": "American",
        "category": "Breakfast",
        "prep_time": 25,
        "difficulty": "Easy",
        "likes": 45,
        "ingredients": [
            "2 cups all-purpose flour",
            "2 tsp baking powder",
            "1/2 tsp baking soda",
            "2 tbsp granulated sugar",
            "1/2 tsp salt",
            "1 3/4 cups buttermilk",
            "2 large eggs",
            "1/4 cup unsalted butter, melted",
            "1 1/2 cups fresh blueberries",
            "Pure maple syrup for serving",
        ],
        "steps": [
            "In a large bowl, whisk together flour, baking powder, baking soda, sugar, and salt.",
            "In a separate bowl, whisk buttermilk, eggs, and melted butter until smooth.",
            "Gently fold the wet ingredients into the dry ingredients until just combined (small lumps are fine).",
            "Heat a lightly greased non-stick griddle over medium heat.",
            "Pour 1/4 cup batter per pancake, scatter fresh blueberries on top, and cook until bubbles form on surface (about 2-3 minutes).",
            "Flip carefully and cook for another 1-2 minutes until golden brown. Serve hot with pure maple syrup.",
        ],
    },
    {
        "title": "Mediterranean Quinoa Power Bowl",
        "cuisine": "Mediterranean",
        "category": "Lunch",
        "prep_time": 25,
        "difficulty": "Easy",
        "likes": 34,
        "ingredients": [
            "1 cup tri-color quinoa, rinsed",
            "1 cup cherry tomatoes, halved",
            "1 English cucumber, diced",
            "1/2 cup Kalamata olives, sliced",
            "1/2 cup crumbled feta cheese",
            "1 can (15 oz) chickpeas, rinsed and drained",
            "3 tbsp extra virgin olive oil",
            "1 tbsp fresh lemon juice",
            "1 clove garlic, minced",
            "1 tsp dried oregano",
        ],
        "steps": [
            "Cook quinoa in 2 cups of water with a pinch of salt until water is absorbed (about 15 minutes), then fluff with a fork and let cool.",
            "Whisk together olive oil, lemon juice, minced garlic, oregano, salt, and pepper in a small bowl for the vinaigrette.",
            "In a large serving bowl, arrange the cooked quinoa, chickpeas, cucumber, cherry tomatoes, and Kalamata olives.",
            "Drizzle the dressing over the bowl and toss lightly to coat.",
            "Garnish with crumbled feta cheese and fresh parsley before serving.",
        ],
    },
    {
        "title": "Classic Margherita Pizza",
        "cuisine": "Italian",
        "category": "Lunch",
        "prep_time": 40,
        "difficulty": "Medium",
        "likes": 52,
        "ingredients": [
            "1 ball artisan pizza dough",
            "1/2 cup San Marzano tomato puree",
            "200g fresh mozzarella cheese, torn",
            "6-8 fresh basil leaves",
            "2 tbsp extra virgin olive oil",
            "1/2 tsp sea salt",
            "Semolina flour for dusting",
        ],
        "steps": [
            "Preheat oven to maximum temperature (around 250°C / 480°F) with a pizza stone or heavy baking tray inside.",
            "Stretch the dough gently by hand on a surface dusted with semolina flour into a 12-inch round disc.",
            "Spread the tomato puree evenly over the dough, leaving a 1/2-inch border for the crust.",
            "Distribute torn fresh mozzarella evenly across the sauce.",
            "Transfer pizza onto the hot stone and bake for 8-10 minutes until the crust is blistered and cheese is melted and bubbling.",
            "Remove from oven, scatter fresh basil leaves on top, drizzle with olive oil, slice and serve immediately.",
        ],
    },
    {
        "title": "Creamy Tuscan Chicken Pasta",
        "cuisine": "Italian",
        "category": "Lunch",
        "prep_time": 30,
        "difficulty": "Medium",
        "likes": 39,
        "ingredients": [
            "2 boneless chicken breasts, sliced",
            "300g fettuccine pasta",
            "1/2 cup sun-dried tomatoes, sliced",
            "3 cups baby spinach",
            "3 cloves garlic, minced",
            "1 cup heavy cream",
            "1/2 cup freshly grated Parmesan cheese",
            "2 tbsp olive oil",
            "1 tsp Italian seasoning",
            "Salt and cracked black pepper",
        ],
        "steps": [
            "Boil pasta in salted water until al dente; reserve 1/2 cup pasta water and drain.",
            "Season chicken strips with Italian seasoning, salt, and pepper; sear in olive oil over medium-high heat until golden brown (about 6 minutes). Set chicken aside.",
            "In the same skillet, sauté minced garlic and sun-dried tomatoes for 1 minute until fragrant.",
            "Pour in heavy cream and bring to a gentle simmer; stir in grated Parmesan until melted and creamy.",
            "Add fresh spinach and cook until wilted, then toss in the cooked pasta and seared chicken.",
            "Stir to coat with sauce (adding splash of reserved pasta water if needed), and serve topped with extra Parmesan.",
        ],
    },
    {
        "title": "Molten Chocolate Lava Cake",
        "cuisine": "French",
        "category": "Dessert",
        "prep_time": 25,
        "difficulty": "Hard",
        "likes": 63,
        "ingredients": [
            "100g dark chocolate (70% cocoa)",
            "100g unsalted butter",
            "2 large whole eggs + 2 egg yolks",
            "1/2 cup powdered sugar",
            "3 tbsp all-purpose flour",
            "1 tsp pure vanilla extract",
            "Pinch of fine sea salt",
            "Vanilla bean ice cream for serving",
        ],
        "steps": [
            "Preheat oven to 200°C (400°F). Butter and dust two 6-ounce ramekins with cocoa powder.",
            "Melt dark chocolate and unsalted butter together in a heatproof bowl set over simmering water; stir until smooth and let cool slightly.",
            "In another bowl, whisk eggs, egg yolks, powdered sugar, vanilla extract, and salt until thick and pale.",
            "Fold the melted chocolate mixture into the egg mixture.",
            "Sift in the flour and gently fold until just incorporated with no dry streaks.",
            "Divide batter into ramekins and bake for 12-14 minutes until sides are set but the center remains soft.",
            "Let rest for 1 minute, invert onto dessert plates, dust with powdered sugar, and serve warm with vanilla ice cream.",
        ],
    },
    {
        "title": "Classic Italian Tiramisu",
        "cuisine": "Italian",
        "category": "Dessert",
        "prep_time": 35,
        "difficulty": "Medium",
        "likes": 47,
        "ingredients": [
            "24 Italian ladyfingers (Savoiardi)",
            "500g mascarpone cheese, chilled",
            "4 large egg yolks",
            "1/2 cup granulated sugar",
            "1 cup heavy whipping cream",
            "1 1/2 cups strong espresso, cooled",
            "2 tbsp coffee liqueur or Marsala wine",
            "3 tbsp unsweetened Dutch cocoa powder",
        ],
        "steps": [
            "Whisk egg yolks and sugar in a heatproof bowl over simmering water for 5 minutes until pale and creamy; let cool.",
            "In a large bowl, beat heavy cream to stiff peaks. In another bowl, gently beat mascarpone until smooth.",
            "Fold the cooled yolk mixture into the mascarpone, then fold in the whipped cream until velvety.",
            "Combine cooled espresso and coffee liqueur in a shallow dish.",
            "Quickly dip each ladyfinger into the coffee mixture (1 second per side) and arrange in a single layer in an 8x8-inch baking dish.",
            "Spread half of the mascarpone cream over the ladyfingers. Repeat with a second dipped ladyfinger layer and remaining cream.",
            "Dust generously with unsweetened cocoa powder and refrigerate for at least 4 hours (or overnight) before slicing.",
        ],
    },
    {
        "title": "Creamy Thai Coconut Chickpea Curry",
        "cuisine": "Thai",
        "category": "Vegan",
        "prep_time": 30,
        "difficulty": "Easy",
        "likes": 58,
        "ingredients": [
            "2 cans (15 oz each) chickpeas, rinsed and drained",
            "1 can (14 oz) full-fat coconut milk",
            "2 tbsp Thai red curry paste",
            "1 medium red bell pepper, thinly sliced",
            "2 cups baby spinach",
            "1 medium onion, diced",
            "3 cloves garlic, minced",
            "1 tbsp fresh ginger, grated",
            "1 tbsp coconut oil",
            "1 tbsp fresh lime juice",
            "Cooked jasmine rice for serving",
        ],
        "steps": [
            "Heat coconut oil in a large pot over medium heat; sauté diced onion, garlic, and ginger until soft and fragrant (about 3 minutes).",
            "Add Thai curry paste and stir constantly for 1 minute to release aromatics.",
            "Pour in coconut milk and stir until the paste dissolves into a fragrant golden sauce.",
            "Add chickpeas and sliced red bell pepper; simmer gently on low heat for 15 minutes to allow flavors to meld.",
            "Stir in baby spinach and fresh lime juice until spinach is wilted.",
            "Season with salt to taste and ladle over steamed jasmine rice.",
        ],
    },
    {
        "title": "Crispy Baked Tofu Buddha Bowl",
        "cuisine": "Asian Fusion",
        "category": "Vegan",
        "prep_time": 35,
        "difficulty": "Medium",
        "likes": 31,
        "ingredients": [
            "400g extra firm tofu, pressed and cubed",
            "2 tbsp cornstarch",
            "1 tbsp tamari or soy sauce",
            "1 tbsp sesame oil",
            "1 cup brown rice, cooked",
            "1 cup shredded purple cabbage",
            "1 cup steamed edamame beans",
            "1 ripe avocado, sliced",
            "2 tbsp peanut tahini dressing",
            "1 tbsp toasted sesame seeds",
        ],
        "steps": [
            "Preheat oven to 200°C (400°F) and line a baking sheet with parchment paper.",
            "Toss pressed tofu cubes with tamari and sesame oil, then sprinkle with cornstarch until evenly coated.",
            "Arrange tofu on the baking sheet in a single layer and bake for 25-30 minutes, flipping halfway, until crispy and golden.",
            "Assemble bowls with cooked grain base, purple cabbage, steamed edamame, and sliced avocado.",
            "Place hot crispy tofu on top, drizzle generously with peanut tahini dressing, and garnish with toasted sesame seeds.",
        ],
    },
]


def seed(db_path: Optional[str] = None) -> None:
    target_path = db_path or get_db_path()
    print(f"Ensuring database schema exists at: {target_path}")
    init_db(target_path)

    conn = sqlite3.connect(target_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    try:
        inserted = 0
        skipped = 0

        for recipe in SAMPLE_RECIPES:
            cursor.execute("SELECT id FROM recipes WHERE title = ?", (recipe["title"],))
            existing = cursor.fetchone()

            if existing:
                skipped += 1
                continue

            cursor.execute(
                """
                INSERT INTO recipes (title, cuisine, category, prep_time, difficulty, likes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    recipe["title"],
                    recipe["cuisine"],
                    recipe["category"],
                    recipe["prep_time"],
                    recipe["difficulty"],
                    recipe["likes"],
                ),
            )
            recipe_id = cursor.lastrowid

            for pos, ing_name in enumerate(recipe["ingredients"]):
                cursor.execute(
                    "INSERT INTO ingredients (recipe_id, name, position) VALUES (?, ?, ?)",
                    (recipe_id, ing_name, pos),
                )

            for pos, step_inst in enumerate(recipe["steps"]):
                cursor.execute(
                    "INSERT INTO steps (recipe_id, instruction, position) VALUES (?, ?, ?)",
                    (recipe_id, step_inst, pos),
                )

            inserted += 1

        conn.commit()
        print(f"Seed complete: {inserted} recipes inserted, {skipped} skipped.")
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
