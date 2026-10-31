// ========================================
// SPENDWISE SA - TRANSACTIONS PAGE
// ========================================


// ========================================
// 1. GLOBAL VARIABLES
// ========================================

let currentPage = 1;
let totalPages = 0;

let currentFilters = {
    search: "",
    type: "",
    reviewOnly: false
};

const pageSize = 20;


// ========================================
// 2. FORMAT CURRENCY
// ========================================

const formatZAR = amount =>
    new Intl.NumberFormat("en-ZA", {
        style: "currency",
        currency: "ZAR"
    }).format(amount);


// ========================================
// 3. DISPLAY TABLE MESSAGE
// ========================================

function showMessage(message) {

    const body = document.getElementById(
        "all-transactions-body"
    );

    body.replaceChildren();

    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = 5;
    cell.className = "table-message";
    cell.textContent = message;

    row.appendChild(cell);
    body.appendChild(row);
}


// ========================================
// 4. RENDER TRANSACTIONS TABLE
// ========================================

function renderTransactions(transactions) {

    const body = document.getElementById(
        "all-transactions-body"
    );

    body.replaceChildren();

    if (!transactions.length) {
        showMessage("No matching transactions found.");
        return;
    }

    transactions.forEach(transaction => {

        const row = document.createElement("tr");

        // Make transaction row clickable
        row.classList.add("clickable-transaction");

        row.tabIndex = 0;
        row.setAttribute("role", "button");

        row.setAttribute(
            "aria-label",
            `View details for transaction ${transaction.transaction_id}`
        );

        row.addEventListener("click", () => {
            openTransactionDetails(transaction.transaction_id);
        });

        row.addEventListener("keydown", event => {

            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                openTransactionDetails(transaction.transaction_id);
            }

        });

        // Transaction information
        const values = [
            transaction.transaction_date || "Unknown",

            transaction.category || "Uncategorized",

            transaction.amount === null
                ? "Not available"
                : formatZAR(transaction.amount),

            transaction.cash_flow_class || "Unclassified"
        ];

        values.forEach((value, index) => {

            const cell = document.createElement("td");
            cell.textContent = value;

            if (index === 2) {

                cell.classList.add("transaction-amount");

                if (transaction.amount > 0) {
                    cell.classList.add("income");
                } else if (transaction.amount < 0) {
                    cell.classList.add("expense");
                }
            }

            row.appendChild(cell);
        });

        // Review status
        const reviewCell = document.createElement("td");
        const badge = document.createElement("span");

        badge.className = transaction.review_required
            ? "review-badge needs-review"
            : "review-badge reviewed";

        badge.textContent = transaction.review_required
            ? "Needs Review"
            : "No Review Needed";

        reviewCell.appendChild(badge);
        row.appendChild(reviewCell);

        body.appendChild(row);
    });
}


// ========================================
// 5. LOAD TRANSACTIONS
// ========================================

async function loadTransactions() {

    const previousButton = document.getElementById(
        "previous-page"
    );

    const nextButton = document.getElementById(
        "next-page"
    );

    previousButton.disabled = true;
    nextButton.disabled = true;

    showMessage("Loading transactions...");

    try {

        const data = await getTransactions({
            page: currentPage,
            pageSize: pageSize,
            ...currentFilters
        });

        totalPages = data.total_pages;

        // If the current page becomes empty after
        // reviewing a transaction, move to a valid page.
        if (totalPages > 0 && currentPage > totalPages) {
            currentPage = totalPages;
            return await loadTransactions();
        }

        renderTransactions(data.transactions);

        document.getElementById(
            "transaction-count"
        ).textContent =
            `${data.total.toLocaleString("en-ZA")} transactions found`;

        document.getElementById(
            "page-indicator"
        ).textContent =
            `Page ${currentPage} of ${Math.max(totalPages, 1)}`;

        previousButton.disabled = currentPage <= 1;
        nextButton.disabled = currentPage >= totalPages;

    } catch (error) {

        console.error(
            "Transaction loading failed:",
            error
        );

        showMessage("Unable to load transactions.");

        document.getElementById(
            "transaction-count"
        ).textContent = "Loading failed";

        document.getElementById(
            "page-indicator"
        ).textContent = "Page unavailable";
    }
}


// ========================================
// 6. INITIALIZE TRANSACTIONS PAGE
// ========================================

document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById(
        "transaction-filter-form"
    );

    // Apply filters
    form.addEventListener("submit", event => {

        event.preventDefault();

        currentPage = 1;

        currentFilters = {
            search: document.getElementById(
                "transaction-search"
            ).value.trim(),

            type: document.getElementById(
                "transaction-type"
            ).value,

            reviewOnly: document.getElementById(
                "review-only"
            ).checked
        };

        loadTransactions();
    });

    // Clear filters
    document.getElementById(
        "clear-filters"
    ).addEventListener("click", () => {

        form.reset();

        currentPage = 1;

        currentFilters = {
            search: "",
            type: "",
            reviewOnly: false
        };

        loadTransactions();
    });

    // Previous page
    document.getElementById(
        "previous-page"
    ).addEventListener("click", () => {

        if (currentPage > 1) {
            currentPage--;
            loadTransactions();
        }
    });

    // Next page
    document.getElementById(
        "next-page"
    ).addEventListener("click", () => {

        if (currentPage < totalPages) {
            currentPage++;
            loadTransactions();
        }
    });

    // Load initial transactions
    loadTransactions();
});


// ========================================
// 7. OPEN TRANSACTION DETAILS PANEL
// ========================================

let detailsRequestId = 0;

async function openTransactionDetails(transactionId) {

    const panel = document.getElementById(
        "transaction-details-panel"
    );

    const overlay = document.getElementById(
        "transaction-overlay"
    );

    const content = document.getElementById(
        "transaction-details-content"
    );

    if (!panel || !overlay || !content) {
        console.error("Transaction details panel not found.");
        return;
    }

    const requestId = ++detailsRequestId;

    // Open panel
    panel.hidden = false;
    overlay.hidden = false;

    panel.classList.add("open");
    overlay.classList.add("visible");

    panel.setAttribute("aria-hidden", "false");

    document.body.classList.add("details-open");

    content.textContent = "Loading transaction details...";

    document.getElementById("close-details").focus();

    try {

        const transaction = await getTransactionDetails(
            transactionId
        );

        // Ignore outdated requests
        if (requestId !== detailsRequestId) {
            return;
        }

        renderTransactionDetails(transaction);

    } catch (error) {

        if (requestId !== detailsRequestId) {
            return;
        }

        console.error(
            "Failed to load transaction details:",
            error
        );

        content.textContent =
            "Unable to load transaction details.";
    }
}


// ========================================
// 8. RENDER TRANSACTION DETAILS
// ========================================

function renderTransactionDetails(transaction) {

    const content = document.getElementById(
        "transaction-details-content"
    );

    // IMPORTANT:
    // Clear previous details BEFORE adding anything.
    content.replaceChildren();


    // ----------------------------------------
    // Helper: Create detail row
    // ----------------------------------------

    function addDetail(label, value) {

        const row = document.createElement("div");
        row.className = "detail-row";

        const labelElement = document.createElement("span");
        labelElement.className = "detail-label";
        labelElement.textContent = label;

        const valueElement = document.createElement("span");
        valueElement.className = "detail-value";

        valueElement.textContent =
            value === null ||
            value === undefined ||
            value === ""
                ? "Not available"
                : String(value);

        row.append(labelElement, valueElement);

        content.appendChild(row);
    }


    // ----------------------------------------
    // Helper: Format money
    // ----------------------------------------

    function money(value) {

        return value === null || value === undefined
            ? "Not available"
            : formatZAR(value);
    }


    // ========================================
    // 8.1 TRANSACTION INFORMATION
    // ========================================

    addDetail(
        "Transaction ID",
        transaction.transaction_id
    );

    addDetail(
        "Statement ID",
        transaction.statement_id
    );

    addDetail(
        "Description",
        transaction.description
    );

    addDetail(
        "Original Description",
        transaction.original_description
    );


    // ========================================
    // 8.2 TRANSACTION DATES
    // ========================================

    addDetail(
        "Transaction Date",
        transaction.transaction_date
    );

    addDetail(
        "Posting Date",
        transaction.posting_date
    );


    // ========================================
    // 8.3 CATEGORY INFORMATION
    // ========================================

    addDetail(
        "Category",
        transaction.category
    );

    addDetail(
        "Parent Category",
        transaction.parent_category
    );

    addDetail(
        "Bank Category",
        transaction.bank_category
    );


    // ========================================
    // 8.4 FINANCIAL INFORMATION
    // ========================================

    addDetail(
        "Transaction Amount",
        money(transaction.transaction_amount)
    );

    addDetail(
        "Money In",
        money(transaction.money_in)
    );

    addDetail(
        "Money Out",
        money(transaction.money_out)
    );

    addDetail(
        "Fee",
        money(transaction.fee)
    );

    addDetail(
        "Balance",
        money(transaction.balance)
    );

    addDetail(
        "Cash Flow",
        money(transaction.cash_flow)
    );


    // ========================================
    // 8.5 CLASSIFICATION
    // ========================================

    addDetail(
        "Transaction Type",
        transaction.transaction_type
    );

    addDetail(
        "Cash Flow Class",
        transaction.cash_flow_class
    );


    // ========================================
    // 8.6 REVIEW STATUS
    // ========================================

    addDetail(
        "Review Status",
        transaction.review_required
            ? "Needs Review"
            : "No Review Needed"
    );


    // ========================================
    // 8.7 ADDITIONAL INFORMATION
    // ========================================

    addDetail(
        "Posting Delay (Days)",
        transaction.posting_delay_days
    );

    addDetail(
        "Created At",
        transaction.created_at
    );


    // ========================================
    // 9. MARK AS REVIEWED BUTTON
    // ========================================

    if (transaction.review_required === true) {

        const reviewButton = document.createElement("button");

        reviewButton.type = "button";
        reviewButton.className = "mark-reviewed-button";
        reviewButton.textContent = "✓ Mark as Reviewed";

        reviewButton.addEventListener("click", async () => {

            reviewButton.disabled = true;
            reviewButton.textContent = "Updating...";

            try {

                await updateTransactionReview(
                    transaction.transaction_id,
                    false
                );

                // Get updated transaction
                const updatedTransaction =
                    await getTransactionDetails(
                        transaction.transaction_id
                    );

                // Refresh details panel
                renderTransactionDetails(updatedTransaction);

                // Refresh table
                await loadTransactions();

                console.log(
                    "Transaction marked as reviewed:",
                    transaction.transaction_id
                );

            } catch (error) {

                console.error(
                    "Failed to update review status:",
                    error
                );

                reviewButton.disabled = false;
                reviewButton.textContent = "✓ Mark as Reviewed";

                alert(
                    "Unable to update transaction review status."
                );
            }
        });

        content.appendChild(reviewButton);
    }


    // ========================================
    // 10. TRANSACTION CATEGORY EDITOR
    // ========================================

    const categoryEditor = document.createElement("div");
    categoryEditor.className = "category-editor";

    // Category label
    const categoryLabel = document.createElement("label");

    categoryLabel.textContent =
        "Change Transaction Category";

    categoryLabel.htmlFor =
        "transaction-category-select";

    // Category dropdown
    const categorySelect = document.createElement("select");

    categorySelect.id =
        "transaction-category-select";

    categorySelect.disabled = true;

    const defaultOption = document.createElement("option");

    defaultOption.value = "";
    defaultOption.textContent = "Loading categories...";

    categorySelect.appendChild(defaultOption);

    // Save button
    const saveCategoryButton = document.createElement("button");

    saveCategoryButton.type = "button";
    saveCategoryButton.className = "save-category-button";
    saveCategoryButton.textContent = "Save Category";
    saveCategoryButton.disabled = true;

    // Status message
    const categoryMessage = document.createElement("p");

    categoryMessage.className = "category-message";
    categoryMessage.setAttribute("role", "status");

    // Add elements to editor
    categoryEditor.appendChild(categoryLabel);
    categoryEditor.appendChild(categorySelect);
    categoryEditor.appendChild(saveCategoryButton);
    categoryEditor.appendChild(categoryMessage);

    // IMPORTANT:
    // Add editor AFTER clearing the content.
    content.appendChild(categoryEditor);


    // ========================================
    // 10.1 LOAD AVAILABLE CATEGORIES
    // ========================================

    getCategories()
        .then(data => {

            // Ignore results for a panel that has
            // already been replaced or closed.
            if (!categoryEditor.isConnected) {
                return;
            }

            categorySelect.replaceChildren();

            data.categories.forEach(category => {

                const option = document.createElement("option");

                option.value = String(category.category_id);
                option.textContent = category.category_name;

                if (
                    Number(category.category_id) ===
                    Number(transaction.category_id)
                ) {
                    option.selected = true;
                }

                categorySelect.appendChild(option);
            });

            categorySelect.disabled = false;

            // Enable saving only if there are categories
            saveCategoryButton.disabled =
                data.categories.length === 0;

        })
        .catch(error => {

            console.error(
                "Unable to load categories:",
                error
            );

            if (!categoryEditor.isConnected) {
                return;
            }

            categoryMessage.textContent =
                "Unable to load categories.";

            categorySelect.disabled = true;
            saveCategoryButton.disabled = true;
        });


    // ========================================
    // 10.2 SAVE SELECTED CATEGORY
    // ========================================

    saveCategoryButton.addEventListener(
        "click",
        async () => {

            const selectedCategoryId =
                Number(categorySelect.value);

            if (!selectedCategoryId) {

                categoryMessage.textContent =
                    "Please select a category.";

                return;
            }

            // Prevent duplicate submissions
            saveCategoryButton.disabled = true;
            categorySelect.disabled = true;

            saveCategoryButton.textContent = "Saving...";
            categoryMessage.textContent = "";

            try {

                await updateTransactionCategory(
                    transaction.transaction_id,
                    selectedCategoryId
                );

                // Get updated transaction
                const updatedTransaction =
                    await getTransactionDetails(
                        transaction.transaction_id
                    );

                // Refresh details panel
                renderTransactionDetails(updatedTransaction);

                // Refresh transactions table
                await loadTransactions();

                console.log(
                    "Transaction category updated:",
                    transaction.transaction_id
                );

            } catch (error) {

                console.error(
                    "Category update failed:",
                    error
                );

                if (categoryEditor.isConnected) {

                    categoryMessage.textContent =
                        "Unable to save category. Please try again.";

                    saveCategoryButton.disabled = false;
                    saveCategoryButton.textContent =
                        "Save Category";

                    categorySelect.disabled = false;
                }
            }
        }
    );
}


// ========================================
// 11. CLOSE TRANSACTION DETAILS PANEL
// ========================================

function closeTransactionDetails() {

    const panel = document.getElementById(
        "transaction-details-panel"
    );

    const overlay = document.getElementById(
        "transaction-overlay"
    );

    if (!panel || !overlay) {
        return;
    }

    // Invalidate any pending details request
    detailsRequestId++;

    panel.classList.remove("open");
    overlay.classList.remove("visible");

    panel.setAttribute("aria-hidden", "true");

    panel.hidden = true;
    overlay.hidden = true;

    document.body.classList.remove("details-open");
}


// ========================================
// 12. INITIALIZE DETAILS PANEL CONTROLS
// ========================================

document.addEventListener("DOMContentLoaded", () => {

    // Close button
    document.getElementById(
        "close-details"
    ).addEventListener(
        "click",
        closeTransactionDetails
    );

    // Close when clicking overlay
    document.getElementById(
        "transaction-overlay"
    ).addEventListener(
        "click",
        closeTransactionDetails
    );

    // Close using Escape
    document.addEventListener("keydown", event => {

        if (event.key === "Escape") {
            closeTransactionDetails();
        }
    });
});