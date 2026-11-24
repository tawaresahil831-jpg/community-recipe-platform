/**
 * Community Recipe Sharing Platform - Client JavaScript
 * Vanilla JS (Zero Build Step, Zero NPM)
 */

// Toast Notifications
function showToast(message, type = "info", duration = 4000) {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "warning") icon = "⚠️";
    if (type === "error") icon = "❌";

    const iconSpan = document.createElement("span");
    iconSpan.textContent = icon;

    const textSpan = document.createElement("span");
    textSpan.textContent = message;

    toast.appendChild(iconSpan);
    toast.appendChild(textSpan);
    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("fade-out");
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ============================================================================
// Explore Feed: Live Debounced Search & Category Filter (templates/index.html)
// ============================================================================
function initExploreFeed() {
    const searchInput = document.getElementById("recipe-search-input");
    const btnClear = document.getElementById("btn-clear-search");
    const categoryChips = document.querySelectorAll(".category-chip");
    const recipeGrid = document.getElementById("recipe-grid");
    const emptyState = document.getElementById("empty-state");
    const countBadge = document.getElementById("recipe-count-badge");
    const headingText = document.getElementById("feed-heading-text");
    const spinner = document.getElementById("search-status-spinner");
    const btnReset = document.getElementById("btn-reset-filters");

    let currentCategory = "all";
    let searchQuery = "";
    let debounceTimer = null;

    // Filter fetch handler
    async function fetchFilteredRecipes() {
        if (spinner) spinner.style.display = "inline-block";

        const params = new URLSearchParams();
        if (currentCategory && currentCategory.toLowerCase() !== "all") {
            params.set("category", currentCategory);
        }
        if (searchQuery.trim()) {
            params.set("q", searchQuery.trim());
        }

        try {
            const url = `/api/recipes?${params.toString()}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error("Failed to load recipes.");

            const recipes = await res.json();
            renderRecipes(recipes);
        } catch (err) {
            showToast(err.message, "error");
        } finally {
            if (spinner) spinner.style.display = "none";
        }
    }

    // Render Recipe Cards safely using textContent to prevent XSS
    function renderRecipes(recipes) {
        if (countBadge) countBadge.textContent = recipes.length;

        if (recipes.length === 0) {
            recipeGrid.style.display = "none";
            emptyState.style.display = "block";
            return;
        }

        emptyState.style.display = "none";
        recipeGrid.style.display = "grid";
        recipeGrid.innerHTML = "";

        recipes.forEach((recipe) => {
            const card = document.createElement("div");
            card.className = "recipe-card";
            card.setAttribute("data-recipe-id", recipe.id);

            // Cover Image
            if (recipe.image) {
                const cover = document.createElement("div");
                cover.className = "recipe-card-cover";
                const img = document.createElement("img");
                img.src = recipe.image;
                img.alt = recipe.title;
                img.loading = "lazy";
                cover.appendChild(img);
                card.appendChild(cover);
            }

            const body = document.createElement("div");
            body.className = "recipe-card-body";

            // 1. Header (Category tag + Difficulty badge)
            const header = document.createElement("div");
            header.className = "recipe-card-header";

            const catTag = document.createElement("span");
            catTag.className = `category-tag tag-${recipe.category.toLowerCase()}`;
            catTag.textContent = recipe.category;

            const diffBadge = document.createElement("span");
            diffBadge.className = `difficulty-badge difficulty-${recipe.difficulty.toLowerCase()}`;
            diffBadge.textContent = recipe.difficulty;

            header.appendChild(catTag);
            header.appendChild(diffBadge);

            // 2. Title
            const titleH3 = document.createElement("h3");
            titleH3.className = "recipe-card-title";
            const titleLink = document.createElement("a");
            titleLink.href = `/recipe/${recipe.id}`;
            titleLink.textContent = recipe.title;
            titleH3.appendChild(titleLink);

            // 3. Meta (Cuisine & Prep time)
            const meta = document.createElement("div");
            meta.className = "recipe-card-meta";

            const cuisineSpan = document.createElement("span");
            cuisineSpan.className = "meta-item";
            cuisineSpan.textContent = `🌍 ${recipe.cuisine}`;

            const separator = document.createElement("span");
            separator.className = "meta-separator";
            separator.textContent = "•";

            const prepSpan = document.createElement("span");
            prepSpan.className = "meta-item";
            prepSpan.textContent = `⏱️ ${recipe.prep_time} mins`;

            meta.appendChild(cuisineSpan);
            meta.appendChild(separator);
            meta.appendChild(prepSpan);

            // 4. Footer (Likes + View link)
            const footer = document.createElement("div");
            footer.className = "recipe-card-footer";

            const likesSpan = document.createElement("span");
            likesSpan.className = "card-likes-count";
            likesSpan.innerHTML = `❤️ <strong>${recipe.likes}</strong> like${recipe.likes === 1 ? "" : "s"}`;

            const viewBtn = document.createElement("a");
            viewBtn.href = `/recipe/${recipe.id}`;
            viewBtn.className = "btn btn-secondary btn-sm";
            viewBtn.textContent = "View Recipe →";

            footer.appendChild(likesSpan);
            footer.appendChild(viewBtn);

            // Assemble card body and card
            body.appendChild(header);
            body.appendChild(titleH3);
            body.appendChild(meta);
            body.appendChild(footer);

            card.appendChild(body);
            recipeGrid.appendChild(card);
        });
    }

    // Debounced search input (300ms)
    if (searchInput) {
        searchInput.addEventListener("input", () => {
            searchQuery = searchInput.value;
            if (btnClear) {
                btnClear.style.display = searchQuery ? "block" : "none";
            }

            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                fetchFilteredRecipes();
            }, 300);
        });
    }

    // Clear search
    if (btnClear) {
        btnClear.addEventListener("click", () => {
            searchInput.value = "";
            searchQuery = "";
            btnClear.style.display = "none";
            searchInput.focus();
            fetchFilteredRecipes();
        });
    }

    // Category chips selection
    categoryChips.forEach((chip) => {
        chip.addEventListener("click", () => {
            categoryChips.forEach((c) => {
                c.classList.remove("active");
                c.setAttribute("aria-selected", "false");
            });
            chip.classList.add("active");
            chip.setAttribute("aria-selected", "true");

            currentCategory = chip.dataset.category;

            if (headingText) {
                headingText.textContent = currentCategory === "all" ? "All Recipes" : `${currentCategory} Recipes`;
            }

            fetchFilteredRecipes();
        });
    });

    // Reset filters
    if (btnReset) {
        btnReset.addEventListener("click", () => {
            searchInput.value = "";
            searchQuery = "";
            if (btnClear) btnClear.style.display = "none";

            categoryChips.forEach((c) => {
                const isAll = c.dataset.category === "all";
                c.classList.toggle("active", isAll);
                c.setAttribute("aria-selected", isAll ? "true" : "false");
            });
            currentCategory = "all";
            if (headingText) headingText.textContent = "All Recipes";

            fetchFilteredRecipes();
        });
    }
}

// ============================================================================
// Recipe Creation Form (templates/create.html)
// ============================================================================
function initCreateRecipeForm() {
    const form = document.getElementById("create-recipe-form");
    if (!form) return;

    const titleInput = document.getElementById("recipe-title-input");
    const titleCounter = document.getElementById("title-char-counter");
    const cuisineInput = document.getElementById("recipe-cuisine-input");
    const categorySelect = document.getElementById("recipe-category-select");
    const prepTimeInput = document.getElementById("recipe-prep-time-input");
    const difficultySelect = document.getElementById("recipe-difficulty-select");

    const ingredientsList = document.getElementById("ingredients-list");
    const btnAddIngredient = document.getElementById("btn-add-ingredient");
    const ingredientsCounter = document.getElementById("ingredients-counter");

    const stepsList = document.getElementById("steps-list");
    const btnAddStep = document.getElementById("btn-add-step");
    const stepsCounter = document.getElementById("steps-counter");

    const errorBanner = document.getElementById("form-error-banner");
    const btnSubmit = document.getElementById("btn-submit-recipe");

    // Live character counter for title
    titleInput.addEventListener("input", () => {
        const len = titleInput.value.length;
        titleCounter.textContent = `${len} / 120`;
        if (len > 0) {
            titleInput.classList.remove("is-invalid");
            const err = document.getElementById("title-error");
            if (err) err.classList.remove("active");
        }
    });

    // Update ingredients numbering & remove button states
    function updateIngredientsUI() {
        const rows = ingredientsList.querySelectorAll(".dynamic-row");
        const count = rows.length;
        ingredientsCounter.textContent = `${count} item${count === 1 ? "" : "s"}`;

        rows.forEach((row, idx) => {
            const num = row.querySelector(".row-num");
            if (num) num.textContent = idx + 1;

            const removeBtn = row.querySelector(".btn-remove-row");
            if (removeBtn) {
                removeBtn.disabled = count <= 1;
                removeBtn.setAttribute("aria-label", `Remove ingredient ${idx + 1}`);
            }
        });
    }

    // Add ingredient row
    btnAddIngredient.addEventListener("click", () => {
        const count = ingredientsList.querySelectorAll(".dynamic-row").length;
        const row = document.createElement("div");
        row.className = "dynamic-row";
        row.innerHTML = `
            <span class="row-num">${count + 1}</span>
            <input
                type="text"
                class="form-control dynamic-input ingredient-input"
                placeholder="e.g. 1 tsp salt"
                maxlength="200"
                required
            >
            <button type="button" class="btn-icon btn-remove-row" title="Remove ingredient">&times;</button>
        `;
        ingredientsList.appendChild(row);
        updateIngredientsUI();

        const input = row.querySelector(".ingredient-input");
        if (input) input.focus();
    });

    // Remove ingredient row
    ingredientsList.addEventListener("click", (e) => {
        const btn = e.target.closest(".btn-remove-row");
        if (!btn) return;
        const rows = ingredientsList.querySelectorAll(".dynamic-row");
        if (rows.length <= 1) return;
        btn.closest(".dynamic-row").remove();
        updateIngredientsUI();
    });

    // Update steps numbering & remove button states
    function updateStepsUI() {
        const rows = stepsList.querySelectorAll(".dynamic-row");
        const count = rows.length;
        stepsCounter.textContent = `${count} step${count === 1 ? "" : "s"}`;

        rows.forEach((row, idx) => {
            const num = row.querySelector(".row-num");
            if (num) num.textContent = `Step ${idx + 1}`;

            const removeBtn = row.querySelector(".btn-remove-row");
            if (removeBtn) {
                removeBtn.disabled = count <= 1;
                removeBtn.setAttribute("aria-label", `Remove step ${idx + 1}`);
            }
        });
    }

    // Add step row
    btnAddStep.addEventListener("click", () => {
        const count = stepsList.querySelectorAll(".dynamic-row").length;
        const row = document.createElement("div");
        row.className = "dynamic-row";
        row.innerHTML = `
            <span class="row-num step-num">Step ${count + 1}</span>
            <textarea
                class="form-control dynamic-input step-input"
                rows="2"
                placeholder="e.g. Mix until smooth..."
                maxlength="200"
                required
            ></textarea>
            <button type="button" class="btn-icon btn-remove-row" title="Remove step">&times;</button>
        `;
        stepsList.appendChild(row);
        updateStepsUI();

        const textarea = row.querySelector(".step-input");
        if (textarea) textarea.focus();
    });

    // Remove step row
    stepsList.addEventListener("click", (e) => {
        const btn = e.target.closest(".btn-remove-row");
        if (!btn) return;
        const rows = stepsList.querySelectorAll(".dynamic-row");
        if (rows.length <= 1) return;
        btn.closest(".dynamic-row").remove();
        updateStepsUI();
    });

    // Form Submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        // Reset errors
        errorBanner.style.display = "none";
        document.querySelectorAll(".field-error").forEach((el) => el.classList.remove("active"));
        document.querySelectorAll(".form-control").forEach((el) => el.classList.remove("is-invalid"));

        const title = titleInput.value.trim();
        const cuisine = cuisineInput.value.trim();
        const category = categorySelect.value;
        const prepTimeStr = prepTimeInput.value.trim();
        const difficulty = difficultySelect.value;

        let hasError = false;

        if (!title) {
            titleInput.classList.add("is-invalid");
            showFieldError("title-error", "Please provide a recipe title.");
            hasError = true;
        }

        if (!cuisine) {
            cuisineInput.classList.add("is-invalid");
            showFieldError("cuisine-error", "Please provide a cuisine type.");
            hasError = true;
        }

        if (!category) {
            categorySelect.classList.add("is-invalid");
            showFieldError("category-error", "Please select a category.");
            hasError = true;
        }

        const prepTime = parseInt(prepTimeStr, 10);
        if (isNaN(prepTime) || prepTime < 1 || prepTime > 1440) {
            prepTimeInput.classList.add("is-invalid");
            showFieldError("prep-time-error", "Prep time must be between 1 and 1440 minutes.");
            hasError = true;
        }

        if (!difficulty) {
            difficultySelect.classList.add("is-invalid");
            showFieldError("difficulty-error", "Please select a difficulty level.");
            hasError = true;
        }

        const ingredientInputs = ingredientsList.querySelectorAll(".ingredient-input");
        const ingredients = [];
        ingredientInputs.forEach((inp) => {
            const val = inp.value.trim();
            if (val) {
                ingredients.push(val);
            } else {
                inp.classList.add("is-invalid");
            }
        });

        if (ingredients.length === 0) {
            showFieldError("ingredients-error", "Please add at least one non-empty ingredient.");
            hasError = true;
        }

        const stepInputs = stepsList.querySelectorAll(".step-input");
        const steps = [];
        stepInputs.forEach((inp) => {
            const val = inp.value.trim();
            if (val) {
                steps.push(val);
            } else {
                inp.classList.add("is-invalid");
            }
        });

        if (steps.length === 0) {
            showFieldError("steps-error", "Please add at least one non-empty step.");
            hasError = true;
        }

        if (hasError) return;

        // Button loading state
        const textContent = btnSubmit.querySelector(".btn-text-content");
        const spinner = btnSubmit.querySelector(".btn-spinner");
        btnSubmit.disabled = true;
        if (textContent) textContent.textContent = "Publishing Recipe...";
        if (spinner) spinner.style.display = "inline-block";

        try {
            const res = await fetch("/api/recipes", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    title,
                    cuisine,
                    category,
                    prep_time: prepTime,
                    difficulty,
                    ingredients,
                    steps,
                }),
            });

            const data = await res.json();
            if (!res.ok) {
                throw new Error(data.error || "Failed to create recipe.");
            }

            showToast("Recipe published successfully! Redirecting...", "success");
            setTimeout(() => {
                window.location.href = `/recipe/${data.id}`;
            }, 500);
        } catch (err) {
            errorBanner.textContent = err.message;
            errorBanner.style.display = "flex";
            btnSubmit.disabled = false;
            if (textContent) textContent.textContent = "Publish Recipe";
            if (spinner) spinner.style.display = "none";
        }
    });

    function showFieldError(id, msg) {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = msg;
            el.classList.add("active");
        }
    }

    updateIngredientsUI();
    updateStepsUI();
}

// ============================================================================
// Recipe Detail Page: Checklist & Like Toggle (templates/recipe.html)
// ============================================================================
function initRecipeDetailPage(recipeId) {
    const checklistItems = document.querySelectorAll(".checklist-item");
    const progressBadge = document.getElementById("checklist-progress");
    const btnResetChecklist = document.getElementById("btn-reset-checklist");

    const btnLike = document.getElementById("btn-like-recipe");
    const likeIcon = document.getElementById("like-icon");
    const likeStatusText = document.getElementById("like-status-text");
    const likeCountBadge = document.getElementById("like-count-badge");
    const likeHint = document.getElementById("like-hint");

    // ------------------------------------------------------------------------
    // 1. Interactive Ingredient Checklist
    // ------------------------------------------------------------------------
    const storageKey = `recipe_${recipeId}_checked_ingredients`;
    let checkedMap = {};

    try {
        const saved = sessionStorage.getItem(storageKey);
        if (saved) checkedMap = JSON.parse(saved);
    } catch (e) {
        checkedMap = {};
    }

    function updateChecklistProgress() {
        const total = checklistItems.length;
        let checkedCount = 0;

        checklistItems.forEach((item) => {
            const checkbox = item.querySelector(".checklist-checkbox");
            const ingId = checkbox.dataset.ingId;

            if (checkedMap[ingId]) {
                checkbox.checked = true;
                item.classList.add("checked");
                checkedCount++;
            } else {
                checkbox.checked = false;
                item.classList.remove("checked");
            }
        });

        if (progressBadge) {
            progressBadge.textContent = `${checkedCount} of ${total} ready`;
            if (checkedCount === total && total > 0) {
                progressBadge.style.backgroundColor = "var(--success-light)";
                progressBadge.style.color = "#047857";
            } else {
                progressBadge.style.backgroundColor = "var(--primary-light)";
                progressBadge.style.color = "var(--primary-hover)";
            }
        }

        try {
            sessionStorage.setItem(storageKey, JSON.stringify(checkedMap));
        } catch (e) {}
    }

    checklistItems.forEach((item) => {
        const checkbox = item.querySelector(".checklist-checkbox");
        checkbox.addEventListener("change", () => {
            const ingId = checkbox.dataset.ingId;
            if (checkbox.checked) {
                checkedMap[ingId] = true;
            } else {
                delete checkedMap[ingId];
            }
            updateChecklistProgress();
        });
    });

    if (btnResetChecklist) {
        btnResetChecklist.addEventListener("click", () => {
            checkedMap = {};
            updateChecklistProgress();
            showToast("Ingredient checklist reset.", "info");
        });
    }

    updateChecklistProgress();

    // ------------------------------------------------------------------------
    // 2. Like / Favorite Button with localStorage & Server Sync
    // ------------------------------------------------------------------------
    const likeStorageKey = "codenova_liked_recipes";
    function getLikedRecipeIds() {
        try {
            const data = localStorage.getItem(likeStorageKey);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            return [];
        }
    }

    function isRecipeLiked(id) {
        const list = getLikedRecipeIds();
        return list.includes(id);
    }

    function setRecipeLiked(id, liked) {
        let list = getLikedRecipeIds();
        if (liked) {
            if (!list.includes(id)) list.push(id);
        } else {
            list = list.filter((item) => item !== id);
        }
        try {
            localStorage.setItem(likeStorageKey, JSON.stringify(list));
        } catch (e) {}
    }

    function renderLikeUI(liked, count) {
        if (likeCountBadge) likeCountBadge.textContent = count;

        if (liked) {
            btnLike.classList.add("liked");
            if (likeIcon) likeIcon.textContent = "❤️";
            if (likeStatusText) likeStatusText.textContent = "Liked";
            if (likeHint) likeHint.textContent = "Click to remove like";
        } else {
            btnLike.classList.remove("liked");
            if (likeIcon) likeIcon.textContent = "🤍";
            if (likeStatusText) likeStatusText.textContent = "Like";
            if (likeHint) likeHint.textContent = "Click to like this recipe";
        }
    }

    // Initialize like UI state from localStorage
    const initiallyLiked = isRecipeLiked(recipeId);
    let currentLikes = parseInt(likeCountBadge ? likeCountBadge.textContent : "0", 10);
    renderLikeUI(initiallyLiked, currentLikes);

    if (btnLike) {
        btnLike.addEventListener("click", async () => {
            const alreadyLiked = isRecipeLiked(recipeId);
            const action = alreadyLiked ? "unlike" : "like";

            // Optimistic UI update
            const nextLiked = !alreadyLiked;
            const optimisticCount = action === "like" ? currentLikes + 1 : Math.max(0, currentLikes - 1);
            renderLikeUI(nextLiked, optimisticCount);
            setRecipeLiked(recipeId, nextLiked);

            btnLike.disabled = true;

            try {
                const res = await fetch(`/api/recipes/${recipeId}/like`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ action }),
                });

                const data = await res.json();
                if (!res.ok) throw new Error(data.error || "Failed to update like.");

                currentLikes = data.likes;
                renderLikeUI(nextLiked, currentLikes);
                showToast(nextLiked ? "Added to your favorites!" : "Removed from favorites.", "success");
            } catch (err) {
                // Revert on error
                setRecipeLiked(recipeId, alreadyLiked);
                renderLikeUI(alreadyLiked, currentLikes);
                showToast(err.message, "error");
            } finally {
                btnLike.disabled = false;
            }
        });
    }
}
