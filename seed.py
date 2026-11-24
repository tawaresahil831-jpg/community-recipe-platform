#!/usr/bin/env python3
"""
Seed script for Community Recipe Sharing Platform.
Provisions 20 distinctive, authentic sample recipes across Breakfast, Lunch, Dessert, and Vegan.
Every recipe has completely unique flavor profiles, cuisines, ingredients, and steps.
Safe to run multiple times (idempotent).
"""

import os
import sqlite3
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from db import init_db, get_db_path

SAMPLE_RECIPES = [
    # -------------------------------------------------------------------------
    # 1. BREAKFAST (5 Recipes)
    # -------------------------------------------------------------------------
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
        "title": "Mediterranean Shakshuka with Feta",
        "cuisine": "Middle Eastern",
        "category": "Breakfast",
        "prep_time": 20,
        "difficulty": "Easy",
        "likes": 37,
        "ingredients": [
            "4 large organic eggs",
            "1 can (14 oz) crushed San Marzano tomatoes",
            "1 medium red bell pepper, diced",
            "1 medium yellow onion, chopped",
            "3 cloves garlic, minced",
            "1 tsp ground cumin & smoked paprika",
            "1/2 cup crumbled feta cheese",
            "Fresh cilantro leaves & crusty pita bread",
        ],
        "steps": [
            "Sauté chopped onion and diced red bell pepper in olive oil in a cast iron skillet for 5 minutes until soft.",
            "Add minced garlic, cumin, and smoked paprika; cook for 1 minute until fragrant.",
            "Pour in crushed tomatoes and simmer gently for 8 minutes until the sauce thickens slightly.",
            "Create 4 small wells in the sauce with a spoon and gently crack an egg into each well.",
            "Cover skillet and simmer on low heat for 5-7 minutes until egg whites are set and yolks remain runny.",
            "Garnish with crumbled feta cheese and fresh cilantro; serve hot straight from the skillet with warm pita.",
        ],
    },
    {
        "title": "Classic French Rolled Herb Omelette",
        "cuisine": "French",
        "category": "Breakfast",
        "prep_time": 15,
        "difficulty": "Medium",
        "likes": 32,
        "ingredients": [
            "3 large farm fresh eggs",
            "2 tbsp high quality unsalted French butter",
            "1 tbsp finely minced fresh chives",
            "1 tbsp chopped fresh tarragon & chervil",
            "Pinch of white pepper and sea salt",
            "Crispy baguette slices for serving",
        ],
        "steps": [
            "Vigorously whisk eggs with a fork in a small bowl until completely smooth with no streaks of white.",
            "Melt butter in an 8-inch non-stick skillet over medium-low heat without browning.",
            "Pour in whisked eggs and shake the pan continuously in small circular motions while gently stirring with a silicone spatula.",
            "When eggs form small velvety curds and top is still glossy (baveuse), remove from heat.",
            "Sprinkle fresh herbs across the center, tilt the pan, and gently roll the omelette into a neat torpedo cylinder.",
            "Invert seam-side down onto a plate, brush the surface with a dot of butter for shine, and serve with baguette.",
        ],
    },
    {
        "title": "Golden Belgian Waffles with Fresh Berries",
        "cuisine": "Belgian",
        "category": "Breakfast",
        "prep_time": 25,
        "difficulty": "Easy",
        "likes": 41,
        "ingredients": [
            "2 cups Belgian waffle flour",
            "2 large eggs, whites and yolks separated",
            "1/2 cup melted unsalted butter",
            "1 3/4 cups warm whole milk",
            "2 tbsp pearl sugar or cane sugar",
            "1 tsp vanilla bean paste",
            "Assorted fresh raspberries, blackberries & whipped cream",
        ],
        "steps": [
            "Preheat your Belgian waffle maker to medium-high heat.",
            "Whisk flour, sugar, and egg yolks with warm milk, melted butter, and vanilla paste until smooth.",
            "In a clean bowl, whip egg whites to stiff peaks; gently fold into the batter with a spatula to keep it airy.",
            "Ladle batter onto the hot waffle iron and close; cook for 4-5 minutes until deep golden brown and crispy.",
            "Serve immediately piled high with fresh berries, a dollop of fresh whipped cream, and a dusting of powdered sugar.",
        ],
    },

    # -------------------------------------------------------------------------
    # 2. LUNCH (5 Recipes)
    # -------------------------------------------------------------------------
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
        "title": "Authentic Japanese Tonkotsu Ramen",
        "cuisine": "Japanese",
        "category": "Lunch",
        "prep_time": 45,
        "difficulty": "Medium",
        "likes": 68,
        "ingredients": [
            "2 portions fresh ramen noodles",
            "4 cups rich tonkotsu pork broth",
            "2 soft-boiled marinated ramen eggs (Ajitsuke Tamago)",
            "4 slices tender braised chashu pork belly",
            "2 sheets roasted nori seaweed",
            "1/2 cup sliced scallions and bamboo shoots (Menma)",
            "1 tbsp black garlic oil (Mayu)",
        ],
        "steps": [
            "Warm the rich tonkotsu broth in a saucepan; season with tare broth seasoning and keep steaming hot.",
            "Boil fresh ramen noodles in rolling boiling water for exactly 90 seconds until chewy (katame).",
            "Divide hot broth into two deep ramen bowls and whisk in a drizzle of black garlic oil.",
            "Drain noodles thoroughly and fold neatly into the broth using chopsticks.",
            "Top each bowl with two slices of chashu pork, a halved marinated egg, crunchy bamboo shoots, and nori sheets.",
        ],
    },
    {
        "title": "Mexican Street Corn Chicken Tacos",
        "cuisine": "Mexican",
        "category": "Lunch",
        "prep_time": 25,
        "difficulty": "Easy",
        "likes": 43,
        "ingredients": [
            "8 small warm corn tortillas",
            "2 cups shredded chipotle chicken breast",
            "1 1/2 cups fire-roasted sweet corn kernels",
            "1/2 cup crumbled Cotija or queso fresco cheese",
            "1/4 cup Mexican crema or sour cream",
            "2 tbsp chopped fresh cilantro",
            "1 tsp chili-lime Tajín seasoning",
            "2 fresh limes, cut into wedges",
        ],
        "steps": [
            "Char sweet corn kernels in a smoking hot dry skillet until slightly blackened and caramelized.",
            "Toss charred corn with Mexican crema, minced cilantro, and a pinch of Tajín seasoning.",
            "Warm corn tortillas directly over an open flame for 20 seconds per side until lightly toasted.",
            "Fill each tortilla with seasoned shredded chipotle chicken.",
            "Spoon the charred street corn mixture generously over the chicken.",
            "Sprinkle with crumbled Cotija cheese and extra cilantro; serve immediately with fresh lime wedges.",
        ],
    },

    # -------------------------------------------------------------------------
    # 3. DESSERT (5 Recipes)
    # -------------------------------------------------------------------------
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
        "title": "New York Strawberry Cheesecake",
        "cuisine": "American",
        "category": "Dessert",
        "prep_time": 60,
        "difficulty": "Hard",
        "likes": 55,
        "ingredients": [
            "2 cups crushed graham cracker crumbs",
            "1/3 cup melted unsalted butter",
            "600g cream cheese, softened to room temperature",
            "3/4 cup granulated sugar",
            "3 large eggs at room temperature",
            "1/2 cup sour cream & 1 tsp lemon zest",
            "1 1/2 cups fresh glazed strawberries for topping",
        ],
        "steps": [
            "Press graham cracker crumbs mixed with melted butter firmly into the bottom of a 9-inch springform pan; chill for 15 minutes.",
            "Beat softened cream cheese and sugar together until completely smooth and free of lumps.",
            "Add eggs one at a time on low speed, followed by sour cream, vanilla, and lemon zest.",
            "Pour batter over crust and bake in a water bath at 160°C (325°F) for 55 minutes until edges are set with a slight center jiggle.",
            "Turn off oven and prop door open 1 inch for 1 hour to prevent cracking; then refrigerate for at least 6 hours.",
            "Top with fresh macerated strawberries in glaze before slicing.",
        ],
    },
    {
        "title": "Japanese Matcha Green Tea Parfait",
        "cuisine": "Japanese",
        "category": "Dessert",
        "prep_time": 20,
        "difficulty": "Medium",
        "likes": 29,
        "ingredients": [
            "2 cups premium matcha green tea ice cream",
            "1/2 cup sweet red bean paste (Anko)",
            "8 chewy glutinous rice balls (Shiratama Dango)",
            "1/2 cup crispy matcha sponge cake cubes",
            "1/4 cup cornflakes or toasted puffed rice",
            "Whipped cream and matcha dusting powder",
        ],
        "steps": [
            "Boil glutinous rice flour dango in water until they float; shock in ice water and drain.",
            "In tall dessert glasses, layer crispy cornflakes at the bottom for crunch.",
            "Add a layer of sweet red bean paste followed by matcha sponge cake cubes.",
            "Scoop velvety matcha ice cream generously over the cake layer.",
            "Garnish the top with chewy shiratama dango, a swirl of whipped cream, and a fine dusting of ceremonial matcha powder.",
        ],
    },
    {
        "title": "Spanish Cinnamon Churros with Chocolate",
        "cuisine": "Spanish",
        "category": "Dessert",
        "prep_time": 30,
        "difficulty": "Medium",
        "likes": 44,
        "ingredients": [
            "1 cup all-purpose flour",
            "1 cup water + 2 tbsp unsalted butter",
            "1 tbsp granulated sugar + 1/2 tsp salt",
            "1 large egg",
            "1/2 cup sugar mixed with 1 tbsp ground cinnamon (for coating)",
            "150g dark Spanish chocolate + 1/2 cup heavy cream (for dipping sauce)",
            "Vegetable oil for frying",
        ],
        "steps": [
            "Bring water, butter, sugar, and salt to a boil in a saucepan. Remove from heat and stir in flour until a smooth ball forms.",
            "Beat in egg until dough is glossy and thick; transfer dough to a piping bag fitted with a large closed star tip.",
            "Heat oil to 180°C (350°F). Pipe 5-inch dough strips directly into hot oil, snipping ends with kitchen shears.",
            "Fry for 2-3 minutes per side until deeply golden and crispy; drain on paper towels.",
            "Immediately roll hot churros in the cinnamon sugar mixture until thoroughly coated.",
            "Melt dark chocolate with heavy cream in a small bowl until thick and glossy; serve warm for dipping.",
        ],
    },

    # -------------------------------------------------------------------------
    # 4. VEGAN (5 Recipes)
    # -------------------------------------------------------------------------
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
            "Preheat oven to 200°C (400°F). Toss pressed tofu cubes with tamari, sesame oil, and cornstarch until evenly coated.",
            "Spread tofu on a parchment-lined baking sheet and bake for 25 minutes, flipping halfway, until golden and crunchy.",
            "Cook brown rice according to package instructions.",
            "Whisk tahini, peanut butter, warm water, maple syrup, and lime juice for the creamy dressing.",
            "Assemble bowls by dividing brown rice, purple cabbage, edamame, and sliced avocado.",
            "Top with crispy baked tofu, drizzle generously with peanut tahini dressing, and finish with toasted sesame seeds.",
        ],
    },
    {
        "title": "North Indian Chana Masala with Naan",
        "cuisine": "Indian",
        "category": "Vegan",
        "prep_time": 35,
        "difficulty": "Medium",
        "likes": 50,
        "ingredients": [
            "2 cans (15 oz each) chickpeas, drained",
            "2 large tomatoes, pureed",
            "1 large yellow onion, finely diced",
            "4 cloves garlic & 1 inch ginger, minced into paste",
            "1 tbsp Chana Masala spice blend (coriander, cumin, amchur)",
            "1/2 tsp ground turmeric and Kashmiri chili powder",
            "2 tbsp neutral oil",
            "Fresh chopped cilantro & warm vegan garlic naan",
        ],
        "steps": [
            "Heat oil in a heavy-bottomed pot; fry cumin seeds until they sputter, then add onions and cook until deep golden brown.",
            "Stir in ginger-garlic paste and cook for 2 minutes until raw aroma dissipates.",
            "Add ground turmeric, Kashmiri chili powder, and Chana Masala spice blend; stir for 30 seconds.",
            "Pour in tomato puree and simmer until oil separates from the masala gravy.",
            "Add drained chickpeas and 1 cup of water; gently crush a few chickpeas with a wooden spoon to thicken the curry.",
            "Simmer for 15 minutes, finish with fresh cilantro and a squeeze of lemon, and serve with warm vegan garlic naan.",
        ],
    },
    {
        "title": "Roasted Butternut Squash & Sage Risotto",
        "cuisine": "Italian",
        "category": "Vegan",
        "prep_time": 40,
        "difficulty": "Medium",
        "likes": 36,
        "ingredients": [
            "1 1/2 cups Carnaroli or Arborio risotto rice",
            "3 cups butternut squash, peeled and diced",
            "5 cups hot vegetable broth",
            "1 medium shallot, minced",
            "1/2 cup dry white wine",
            "8 fresh sage leaves",
            "3 tbsp nutritional yeast (for rich cheesy flavor)",
            "3 tbsp extra virgin olive oil",
        ],
        "steps": [
            "Toss half of the butternut squash cubes with olive oil and roast at 200°C (400°F) for 25 minutes until caramelized.",
            "Boil the remaining squash in vegetable broth until fork tender; blend into a smooth golden puree.",
            "Sauté shallots in olive oil in a wide pan until translucent; add rice and toast for 2 minutes until edges are translucent.",
            "Deglaze pan with white wine, stirring constantly until fully absorbed.",
            "Add hot vegetable broth one ladle at a time, stirring gently until each ladle is absorbed before adding the next (about 18 minutes).",
            "Stir in the squash puree, nutritional yeast, and crispy pan-fried sage leaves; top with roasted squash cubes and serve hot.",
        ],
    },
    {
        "title": "Fresh Vietnamese Summer Spring Rolls",
        "cuisine": "Vietnamese",
        "category": "Vegan",
        "prep_time": 25,
        "difficulty": "Easy",
        "likes": 42,
        "ingredients": [
            "10 round rice paper wrappers (Bánh tráng)",
            "100g thin rice vermicelli noodles, cooked and cooled",
            "1 cup crispy marinated baked tofu strips",
            "1 cup shredded carrots and cucumber matchsticks",
            "1 cup fresh mint leaves, Thai basil & cilantro",
            "1/2 cup creamy hoisin peanut dipping sauce",
            "1 tbsp crushed roasted peanuts for garnish",
        ],
        "steps": [
            "Dip one sheet of rice paper wrapper in warm water for 5 seconds until pliable; lay flat on a clean damp cutting board.",
            "Place fresh mint, Thai basil, and cilantro leaves horizontally in the center of the wrapper.",
            "Layer rice vermicelli noodles, crispy tofu strips, cucumber, and shredded carrots on top of the herbs.",
            "Fold the bottom edge firmly over the filling, fold in both sides tightly, and roll forward into a snug cylinder.",
            "Repeat with remaining wrappers and ingredients.",
            "Serve fresh rolls immediately accompanied by rich hoisin peanut dipping sauce sprinkled with crushed peanuts.",
        ],
    },
]


def seed(db_path: Optional[str] = None) -> None:
    """Insert the 20 diverse sample recipes into the database idempotently."""
    target_path = db_path or get_db_path()
    init_db(target_path)

    conn = sqlite3.connect(
        target_path,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
    )
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
