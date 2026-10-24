// ----------------------------------------
// SPENDWISE SA - TRANSACTIONS PAGE
// ----------------------------------------

let currentPage = 1;
let totalPages = 0;
let currentFilters = {
    search: "",
    type: "",
    reviewOnly: false
};

const pageSize = 20;

const formatZAR = amount =>
    new Intl.NumberFormat("en-ZA", {
        style: "currency",
        currency: "ZAR"
    }).format(amount);


// ----------------------------------------
// Display table message
// ----------------------------------------

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


// ----------------------------------------
// Render transactions
// ----------------------------------------

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


// ----------------------------------------
// Load transactions from API
// ----------------------------------------

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

        console.error("Transaction loading failed:", error);

        showMessage("Unable to load transactions.");

        document.getElementById(
            "transaction-count"
        ).textContent = "Loading failed";

        document.getElementById(
            "page-indicator"
        ).textContent = "Page unavailable";
    }
}


// ----------------------------------------
// Initialize page
// ----------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById(
        "transaction-filter-form"
    );

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

    document.getElementById(
        "previous-page"
    ).addEventListener("click", () => {

        if (currentPage > 1) {
            currentPage--;
            loadTransactions();
        }
    });

    document.getElementById(
        "next-page"
    ).addEventListener("click", () => {

        if (currentPage < totalPages) {
            currentPage++;
            loadTransactions();
        }
    });

    loadTransactions();
});