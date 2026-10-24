
// ----------------------------------------
// SPENDWISE SA - DASHBOARD
// ----------------------------------------

// ----------------------------------------
// 1. Formatting helpers
// ----------------------------------------

function formatCurrency(amount) {
    return new Intl.NumberFormat("en-ZA", {
        style: "currency",
        currency: "ZAR"
    }).format(amount);
}

function formatNumber(value) {
    return new Intl.NumberFormat("en-ZA").format(value);
}


// ----------------------------------------
// 2. Load dashboard summary cards
// ----------------------------------------

async function loadDashboardSummary() {
    try {
        const [transactions, finances] = await Promise.all([
            getTransactionSummary(),
            getFinancialSummary()
        ]);

        document.getElementById("total-income").textContent =
            formatCurrency(finances.classified_income);

        document.getElementById("total-expenses").textContent =
            formatCurrency(finances.classified_expenses);

        document.getElementById("total-transactions").textContent =
            formatNumber(transactions.total_transactions);

        document.getElementById("review-count").textContent =
            formatNumber(transactions.review_required);

        console.log("Dashboard summary loaded successfully.");

    } catch (error) {
        console.error("Dashboard loading failed:", error);

        document.getElementById("total-income").textContent =
            "Unavailable";

        document.getElementById("total-expenses").textContent =
            "Unavailable";

        document.getElementById("total-transactions").textContent =
            "Unavailable";

        document.getElementById("review-count").textContent =
            "Unavailable";
    }
}


// ----------------------------------------
// 3. Spending by Category chart
// ----------------------------------------

async function loadCategoryChart() {
    try {
        const data = await getSpendingByCategory();

        const categories = data.categories;

        const labels = categories.map(
            item => item.category
        );

        const amounts = categories.map(
            item => item.total_spending
        );

        const canvas = document.getElementById(
            "category-chart"
        );

        if (!canvas) {
            throw new Error("Category chart canvas not found.");
        }

        new Chart(canvas, {
            type: "doughnut",

            data: {
                labels: labels,

                datasets: [{
                    label: "Spending (ZAR)",
                    data: amounts,

                    backgroundColor: [
                        "#10b981",
                        "#14263d",
                        "#38bdf8",
                        "#f59e0b",
                        "#8b5cf6",
                        "#ef4444",
                        "#14b8a6",
                        "#6366f1",
                        "#f97316",
                        "#94a3b8"
                    ],

                    borderWidth: 2,
                    borderColor: "#ffffff"
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        position: "bottom",

                        labels: {
                            boxWidth: 12,
                            padding: 12
                        }
                    },

                    tooltip: {
                        callbacks: {
                            label: function (context) {

                                // Spending amount for selected category
                                const amount = Number(context.parsed);

                                // Calculate total category spending
                                const total = context.dataset.data.reduce(
                                    (sum, value) => sum + Number(value),
                                    0
                                );

                                // Calculate percentage of total spending
                                const percentage = total > 0
                                    ? ((amount / total) * 100).toFixed(1)
                                    : "0.0";

                                // Display amount and percentage
                                return context.label + ": " +
                                    formatCurrency(amount) +
                                    " (" + percentage +
                                    "% of total spending)";
                            }
                        }
                    }
                }
            }
        });

        console.log("Category chart loaded successfully.");

    } catch (error) {
        console.error("Category chart loading failed:", error);
    }
}


// ----------------------------------------
// 4. Monthly Income vs Expenses chart
// ----------------------------------------

async function loadMonthlyCashFlowChart() {
    try {
        const data = await getMonthlyCashFlow();

        const records = data.monthly_cash_flow;

        const labels = records.map(
            item => item.month
        );

        const income = records.map(
            item => item.income
        );

        const expenses = records.map(
            item => item.expenses
        );

        const canvas = document.getElementById(
            "cash-flow-chart"
        );

        if (!canvas) {
            throw new Error("Cash-flow chart canvas not found.");
        }

        new Chart(canvas, {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Classified Income",
                        data: income,
                        backgroundColor: "#10b981",
                        borderRadius: 5
                    },

                    {
                        label: "Classified Expenses",
                        data: expenses,
                        backgroundColor: "#14263d",
                        borderRadius: 5
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    mode: "index",
                    intersect: false
                },

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            callback: value =>
                                "R " + Number(value).toLocaleString("en-ZA")
                        }
                    }
                },

                plugins: {
                    legend: {
                        position: "bottom"
                    },

                    tooltip: {
                        callbacks: {
                            label: function (context) {
                                return context.dataset.label + ": " +
                                    formatCurrency(context.parsed.y);
                            }
                        }
                    }
                }
            }
        });

        console.log("Monthly cash-flow chart loaded successfully.");

    } catch (error) {
        console.error("Monthly cash-flow chart error:", error);
    }
}


// ----------------------------------------
// 5. Monthly Spending Trend chart
// ----------------------------------------

async function loadMonthlySpendingChart() {
    try {
        const data = await getMonthlySpending();

        const records = data.monthly_spending;

        const labels = records.map(
            item => item.month
        );

        const spending = records.map(
            item => item.total_spending
        );

        const canvas = document.getElementById(
            "monthly-spending-chart"
        );

        if (!canvas) {
            throw new Error(
                "Monthly spending chart canvas not found."
            );
        }

        new Chart(canvas, {
            type: "line",

            data: {
                labels: labels,

                datasets: [{
                    label: "Monthly Spending",
                    data: spending,

                    borderColor: "#10b981",
                    backgroundColor: "rgba(16, 185, 129, 0.12)",

                    borderWidth: 3,
                    tension: 0.35,

                    fill: true,

                    pointRadius: 4,
                    pointHoverRadius: 7,
                    pointBackgroundColor: "#10b981"
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    mode: "index",
                    intersect: false
                },

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            callback: value =>
                                "R " + Number(value).toLocaleString("en-ZA")
                        }
                    }
                },

                plugins: {
                    legend: {
                        position: "bottom"
                    },

                    tooltip: {
                        callbacks: {
                            label: function (context) {

                                // Line charts use parsed.y
                                const amount = context.parsed.y;

                                return "Monthly Spending: " +
                                    formatCurrency(amount);
                            }
                        }
                    }
                }
            }
        });

        console.log(
            "Monthly spending chart loaded successfully."
        );

    } catch (error) {
        console.error("Monthly spending chart error:", error);
    }
}


// ----------------------------------------
// Load recent transactions
// ----------------------------------------

async function loadRecentTransactions() {

    const tableBody = document.getElementById(
        "recent-transactions-body"
    );

    if (!tableBody) {
        return;
    }

    try {
        const data = await getRecentTransactions();

        const transactions = data.recent_transactions;

        tableBody.replaceChildren();

        if (!transactions || transactions.length === 0) {
            showTransactionMessage(
                tableBody,
                "No transactions found."
            );
            return;
        }

        transactions.forEach(transaction => {

            const row = document.createElement("tr");

            // Date
            const dateCell = document.createElement("td");

            dateCell.textContent = transaction.transaction_date
                ? transaction.transaction_date
                : "Unknown";

            // Category
            const categoryCell = document.createElement("td");

            categoryCell.textContent =
                transaction.category || "Uncategorized";

            // Amount
            const amountCell = document.createElement("td");

            amountCell.className = "transaction-amount";

            if (transaction.amount === null) {
                amountCell.textContent = "Not available";
            } else {
                amountCell.textContent = formatCurrency(
                    transaction.amount
                );

                if (transaction.amount > 0) {
                    amountCell.classList.add("income");
                } else if (transaction.amount < 0) {
                    amountCell.classList.add("expense");
                }
            }

            // Transaction type
            const typeCell = document.createElement("td");

            typeCell.textContent =
                transaction.cash_flow_class || "Unclassified";

            // Review status
            const reviewCell = document.createElement("td");

            const reviewBadge = document.createElement("span");

            reviewBadge.className = transaction.review_required
                ? "review-badge needs-review"
                : "review-badge reviewed";

            reviewBadge.textContent = transaction.review_required
                ? "Needs Review"
                : "No Review Needed";

            reviewCell.appendChild(reviewBadge);

            row.append(
                dateCell,
                categoryCell,
                amountCell,
                typeCell,
                reviewCell
            );

            tableBody.appendChild(row);
        });

        console.log("Recent transactions loaded successfully.");

    } catch (error) {
        console.error(
            "Failed to load recent transactions:",
            error
        );

        tableBody.replaceChildren();

        showTransactionMessage(
            tableBody,
            "Unable to load recent transactions."
        );
    }
}


// ----------------------------------------
// Display table messages
// ----------------------------------------

function showTransactionMessage(tableBody, message) {

    const row = document.createElement("tr");
    const cell = document.createElement("td");

    cell.colSpan = 5;
    cell.className = "table-message";
    cell.textContent = message;

    row.appendChild(cell);
    tableBody.appendChild(row);
}

// ----------------------------------------
// 6. Initialise dashboard
// ----------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    loadDashboardSummary();
    loadCategoryChart();
    loadMonthlyCashFlowChart();
    loadMonthlySpendingChart();
    loadRecentTransactions();
});