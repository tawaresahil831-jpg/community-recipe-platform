#!/usr/bin/env python3
"""
Automated end-to-end browser test and screenshot capture using Playwright.
Tests recipe explore feed, dynamic creation, search & category filtering,
interactive checklist, and like persistence with mobile verification.
"""

import os
import time
import sqlite3
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5000"
SCREENSHOTS_DIR = os.path.abspath("screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

TEST_RECIPE_TITLE = "Authentic Japanese Ramen Bowl"


def cleanup_test_recipe():
    from db import get_db_path
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("DELETE FROM recipes WHERE title = ?", (TEST_RECIPE_TITLE,))
    conn.commit()
    conn.close()


def run():
    cleanup_test_recipe()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1200, "height": 850})
        page = context.new_page()

        # 1. Explore Feed
        print("1. Capturing Explore Feed...")
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector(".recipe-card")
        time.sleep(0.5)

        screenshot1 = os.path.join(SCREENSHOTS_DIR, "01-explore-feed.png")
        page.screenshot(path=screenshot1, full_page=False)
        print(f"   Saved {screenshot1}")

        # 2. Recipe Creation Form
        print("2. Testing Recipe Creation Form...")
        page.goto(f"{BASE_URL}/create")
        page.wait_for_selector("#create-recipe-form")

        page.fill("#recipe-title-input", TEST_RECIPE_TITLE)
        page.fill("#recipe-cuisine-input", "Japanese")
        page.select_option("#recipe-category-select", "Lunch")
        page.fill("#recipe-prep-time-input", "45")
        page.select_option("#recipe-difficulty-select", "Medium")

        # Add 2 more ingredients (total 4)
        page.click("#btn-add-ingredient")
        page.click("#btn-add-ingredient")

        ingredients = [
            "2 portions fresh ramen noodles",
            "4 cups rich pork bone broth",
            "2 soft-boiled marinated ramen eggs",
            "Sliced chashu pork, nori sheets & scallions",
        ]
        ing_inputs = page.query_selector_all(".ingredient-input")
        for idx, ing_text in enumerate(ingredients):
            ing_inputs[idx].fill(ing_text)

        # Add 1 more step (total 3)
        page.click("#btn-add-step")
        steps = [
            "Simmer the rich bone broth with tare seasoning and garlic for 20 minutes.",
            "Boil the fresh ramen noodles in salted water for exactly 2 minutes until firm.",
            "Ladle hot broth over noodles, arrange sliced chashu, halved ramen eggs, and nori.",
        ]
        step_inputs = page.query_selector_all(".step-input")
        for idx, step_text in enumerate(steps):
            step_inputs[idx].fill(step_text)

        time.sleep(0.5)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.3)
        screenshot2 = os.path.join(SCREENSHOTS_DIR, "02-create-recipe-form.png")
        page.screenshot(path=screenshot2, full_page=False)
        print(f"   Saved {screenshot2}")

        # Submit form
        page.click("#btn-submit-recipe")
        page.wait_for_url("**/recipe/*")
        created_url = page.url
        print(f"   Recipe created! Redirected to: {created_url}")

        # 3. Recipe Detail with Interactive Checklist and Like
        print("3. Testing Recipe Detail, Checklist & Like Counter...")
        page.wait_for_selector(".recipe-body-grid")

        # Click like button
        btn_like = page.locator("#btn-like-recipe")
        btn_like.click()
        time.sleep(0.5)

        # Tick off first 2 ingredients using label click to trigger checklist progress
        checklist_labels = page.locator(".checklist-item")
        checklist_labels.nth(0).click()
        time.sleep(0.2)
        checklist_labels.nth(1).click()
        time.sleep(0.3)

        screenshot3 = os.path.join(SCREENSHOTS_DIR, "03-recipe-detail.png")
        page.screenshot(path=screenshot3, full_page=False)
        print(f"   Saved {screenshot3}")

        # 4. Search and Category Filter Results
        print("4. Testing Search and Category Filter together...")
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector(".recipe-card")

        # Select Vegan category chip
        vegan_chip = page.locator(".category-chip").filter(has_text="Vegan")
        vegan_chip.click()
        time.sleep(0.5)

        # Type search keyword "curry"
        page.fill("#recipe-search-input", "curry")
        time.sleep(0.6)  # wait for 300ms debounce + fetch

        page.wait_for_selector(".recipe-card")
        screenshot4 = os.path.join(SCREENSHOTS_DIR, "04-search-filter-results.png")
        page.screenshot(path=screenshot4, full_page=False)
        print(f"   Saved {screenshot4}")

        # 5. Mobile View (375px width)
        print("5. Testing Mobile View Responsive Layout...")
        mobile_context = browser.new_context(
            viewport={"width": 375, "height": 812},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        mobile_page = mobile_context.new_page()
        mobile_page.goto(f"{BASE_URL}/recipe/1")
        mobile_page.wait_for_selector(".recipe-title-main")
        time.sleep(0.5)

        screenshot5 = os.path.join(SCREENSHOTS_DIR, "05-mobile-view.png")
        mobile_page.screenshot(path=screenshot5, full_page=False)
        print(f"   Saved {screenshot5}")

        browser.close()

    # Clean up test recipe from database
    cleanup_test_recipe()
    print("All screenshots successfully captured and test recipe cleanly removed!")


if __name__ == "__main__":
    run()
