PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    cuisine TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Breakfast', 'Lunch', 'Dessert', 'Vegan')),
    prep_time INTEGER NOT NULL CHECK (prep_time >= 1 AND prep_time <= 1440),
    difficulty TEXT NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    likes INTEGER NOT NULL DEFAULT 0 CHECK (likes >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    instruction TEXT NOT NULL,
    position INTEGER NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ingredients_recipe_id ON ingredients (recipe_id);
CREATE INDEX IF NOT EXISTS idx_steps_recipe_id ON steps (recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes (category);
CREATE INDEX IF NOT EXISTS idx_recipes_title ON recipes (title);
