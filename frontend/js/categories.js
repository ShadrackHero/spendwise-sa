
"use strict";

// ========================================
// SPENDWISE SA - CATEGORIES MANAGEMENT
// CHAPTER 14
// ========================================

// const API_BASE_URL = "http://127.0.0.1:8000";

let allCategories = [];
let categoriesLoaded = false;
let categoryDetailsRequestId = 0;


// ========================================
// FORMAT CURRENCY AND NUMBERS
// ========================================

function formatCategoryCurrency(amount) {
    return new Intl.NumberFormat("en-ZA", {
        style: "currency",
        currency: "ZAR"
    }).format(Number(amount) || 0);
}

function formatCategoryNumber(value) {
    return new Intl.NumberFormat("en-ZA").format(
        Number(value) || 0
    );
}


// ========================================
// LOAD CATEGORY SUMMARY CARDS
// ========================================

async function loadCategoriesSummary() {

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/categories/summary`
        );

        if (!response.ok) {
            throw new Error(
                `Summary API failed: ${response.status}`
            );
        }

        const data = await response.json();

        document.getElementById("total-categories").textContent =
            formatCategoryNumber(data.total_categories);

        document.getElementById("categorized-transactions").textContent =
            formatCategoryNumber(data.categorized_transactions);

        document.getElementById("uncategorized-transactions").textContent =
            formatCategoryNumber(data.uncategorized_transactions);

        document.getElementById("category-total-expenses").textContent =
            formatCategoryCurrency(data.total_expenses);

        console.log("Categories summary loaded successfully.");

    } catch (error) {

        console.error("Categories summary loading failed:", error);

        [
            "total-categories",
            "categorized-transactions",
            "uncategorized-transactions",
            "category-total-expenses"
        ].forEach(id => {
            document.getElementById(id).textContent = "Error";
        });
    }
}


// ========================================
// DISPLAY CATEGORY TABLE ROWS
// ========================================

function renderCategories(categories) {

    const tableBody = document.getElementById(
        "categories-table-body"
    );

    const categoryCount = document.getElementById(
        "category-count"
    );

    tableBody.replaceChildren();

    categoryCount.textContent =
        `${formatCategoryNumber(categories.length)} categories found`;

    if (categories.length === 0) {

        const row = tableBody.insertRow();
        const cell = row.insertCell();

        cell.colSpan = 4;
        cell.className = "table-message";
        cell.textContent = "No matching categories found.";

        return;
    }

    categories.forEach(category => {

        const row = tableBody.insertRow();

        // Make the entire row clickable
        row.style.cursor = "pointer";
        row.tabIndex = 0;
        row.setAttribute("role", "button");
        row.setAttribute(
            "aria-label",
            `View details for ${category.category_name}`
        );

        row.addEventListener("click", () => {
            openCategoryDetails(category.category_id);
        });

        // Support keyboard navigation
        row.addEventListener("keydown", event => {

            if (
                event.key === "Enter" ||
                event.key === " "
            ) {
                event.preventDefault();
                openCategoryDetails(category.category_id);
            }
        });

        row.insertCell().textContent =
            category.category_name;

        row.insertCell().textContent =
            formatCategoryNumber(category.transaction_count);

        row.insertCell().textContent =
            formatCategoryCurrency(category.total_expenses);

        row.insertCell().textContent =
            `${Number(category.expense_percentage).toFixed(2)}%`;
    });
}


// ========================================
// LOAD CATEGORIES TABLE
// ========================================

async function loadCategoriesTable() {

    const tableBody = document.getElementById(
        "categories-table-body"
    );

    const categoryCount = document.getElementById(
        "category-count"
    );

    categoriesLoaded = false;

    try {

        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="table-message">
                    Loading categories...
                </td>
            </tr>
        `;

        const response = await fetch(
            `${API_BASE_URL}/api/categories/statistics`
        );

        if (!response.ok) {
            throw new Error(
                `Statistics API failed: ${response.status}`
            );
        }

        const data = await response.json();

        allCategories = data.categories;
        categoriesLoaded = true;

        // Preserve a search entered during loading
        const searchInput = document.getElementById(
            "category-search"
        );

        filterCategories(searchInput.value);

        console.log(
            "Categories table loaded successfully:",
            allCategories.length
        );

    } catch (error) {

        console.error("Categories table loading failed:", error);

        categoryCount.textContent =
            "Unable to load categories.";

        tableBody.replaceChildren();

        const row = tableBody.insertRow();
        const cell = row.insertCell();

        cell.colSpan = 4;
        cell.className = "table-message";
        cell.textContent = "Failed to load category information.";
    }
}


// ========================================
// CATEGORY SEARCH AND FILTERING
// ========================================

function filterCategories(searchTerm) {

    if (!categoriesLoaded) {
        return;
    }

    const term = searchTerm.toLowerCase().trim();

    const filteredCategories = allCategories.filter(category =>
        category.category_name.toLowerCase().includes(term)
    );

    renderCategories(filteredCategories);
}


// ========================================
// OPEN CATEGORY DETAILS PANEL
// ========================================

async function openCategoryDetails(categoryId) {

    console.log("Opening category details:", categoryId);

    const overlay = document.getElementById(
        "category-overlay"
    );

    const panel = document.getElementById(
        "category-details-panel"
    );

    const title = document.getElementById(
        "category-details-title"
    );

    const content = document.getElementById(
        "category-details-content"
    );

    // Check that the HTML elements exist
    if (!overlay || !panel || !title || !content) {

        console.error(
            "Category details panel HTML elements are missing."
        );

        alert(
            "Category details panel is missing. Check categories.html."
        );

        return;
    }

    // Track requests to prevent stale responses
    const requestId = ++categoryDetailsRequestId;

    overlay.hidden = false;
    panel.hidden = false;

    title.textContent = "Category Details";
    content.textContent = "Loading category details...";

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/categories/${categoryId}`
        );

        if (!response.ok) {
            throw new Error(
                `Category details API failed: ${response.status}`
            );
        }

        const category = await response.json();

        if (
            panel.hidden ||
            requestId !== categoryDetailsRequestId
        ) {
            return;
        }

        title.textContent = category.category_name;

        content.replaceChildren();

        const details = [
            ["Category ID", category.category_id],
            [
                "Description",
                category.description || "No description"
            ],
            [
                "Transactions",
                formatCategoryNumber(category.transaction_count)
            ],
            [
                "Total Expenses",
                formatCategoryCurrency(category.total_expenses)
            ],
            [
                "Total Income",
                formatCategoryCurrency(category.total_income)
            ]
        ];

        details.forEach(([label, value]) => {

            const item = document.createElement("div");
            item.className = "detail-item";

            const labelElement = document.createElement("strong");
            labelElement.textContent = label;

            const valueElement = document.createElement("p");
            valueElement.textContent = value;

            item.append(labelElement, valueElement);

            content.appendChild(item);
        });

        console.log(
            "Category details loaded:",
            category.category_name
        );

    } catch (error) {

        console.error("Category details loading failed:", error);

        if (
            !panel.hidden &&
            requestId === categoryDetailsRequestId
        ) {
            content.textContent =
                "Unable to load category details.";
        }
    }
}


// ========================================
// CLOSE CATEGORY DETAILS PANEL
// ========================================

function closeCategoryDetails() {

    const overlay = document.getElementById(
        "category-overlay"
    );

    const panel = document.getElementById(
        "category-details-panel"
    );

    // Invalidate any pending details request
    categoryDetailsRequestId++;

    if (overlay) {
        overlay.hidden = true;
    }

    if (panel) {
        panel.hidden = true;
    }
}


// ========================================
// INITIALIZE CATEGORIES PAGE
// ========================================

document.addEventListener("DOMContentLoaded", () => {

    // Load summary cards and categories
    loadCategoriesSummary();
    loadCategoriesTable();

    const searchForm = document.getElementById(
        "category-filter-form"
    );

    const searchInput = document.getElementById(
        "category-search"
    );

    const clearButton = document.getElementById(
        "clear-category-filters"
    );

    // Search categories
    searchForm.addEventListener("submit", event => {

        event.preventDefault();

        filterCategories(searchInput.value);
    });

    // Clear category search
    clearButton.addEventListener("click", () => {

        searchInput.value = "";

        filterCategories("");
    });

    // Close category details with X button
    const closeButton = document.getElementById(
        "close-category-details"
    );

    if (closeButton) {
        closeButton.addEventListener(
            "click",
            closeCategoryDetails
        );
    }

    // Close category details by clicking overlay
    const overlay = document.getElementById(
        "category-overlay"
    );

    if (overlay) {
        overlay.addEventListener(
            "click",
            closeCategoryDetails
        );
    }

    // Close category details using Escape
    document.addEventListener("keydown", event => {

        if (event.key === "Escape") {
            closeCategoryDetails();
        }
    });

    console.log("SpendWise SA Categories page initialized.");
});
