
// ----------------------------------------
// SPENDWISE SA - FINANCIAL INSIGHTS
// CHAPTER 15
// ----------------------------------------

function formatInsightsCurrency(amount) {
    return new Intl.NumberFormat("en-ZA", {
        style: "currency",
        currency: "ZAR"
    }).format(amount);
}

// ----------------------------------------
// Load monthly financial insights
// ----------------------------------------

async function loadFinancialInsights() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/analytics/monthly`
        );

        if (!response.ok) {
            throw new Error(
                `API request failed: ${response.status}`
            );
        }

        const data = await response.json();
        const months = data.months;

        if (!Array.isArray(months)) {
            throw new Error("Invalid monthly analytics response");
        }

        // Calculate summary totals
        const totalIncome = months.reduce(
            (sum, month) => sum + month.total_income,
            0
        );

        const totalExpenses = months.reduce(
            (sum, month) => sum + month.total_expenses,
            0
        );

        const netCashFlow = totalIncome - totalExpenses;

        // Update summary cards
        document.getElementById(
            "insights-total-income"
        ).textContent = formatInsightsCurrency(totalIncome);

        document.getElementById(
            "insights-total-expenses"
        ).textContent = formatInsightsCurrency(totalExpenses);

        document.getElementById(
            "insights-net-cash-flow"
        ).textContent = formatInsightsCurrency(netCashFlow);

        document.getElementById(
            "insights-total-months"
        ).textContent = data.total_months;

        // Populate monthly table
        const tableBody = document.getElementById(
            "insights-table-body"
        );

        tableBody.innerHTML = "";

        if (months.length === 0) {
            tableBody.innerHTML = `
                 <tr>
                     <td colspan="4" class="table-message">
                         No monthly financial data available.
                     </td>
                 </tr>
             `;
            return;
        }

        months.forEach(month => {
            const row = document.createElement("tr");

            const values = [
                month.month,
                formatInsightsCurrency(month.total_income),
                formatInsightsCurrency(month.total_expenses),
                formatInsightsCurrency(month.net_cash_flow)
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value;
                row.appendChild(cell);
            });

            tableBody.appendChild(row);
        });

        renderIncomeExpensesChart(months);
        renderNetCashFlowChart(months);
        console.log("Financial insights loaded successfully.");

    } catch (error) {
        console.error("Financial insights loading failed:", error);

        document.getElementById(
            "insights-table-body"
        ).innerHTML = `
             <tr>
                 <td colspan="4" class="table-message">
                     Unable to load financial insights.
                 </td>
             </tr>
         `;
    }
}


// ----------------------------------------
// Monthly Income vs Expenses Chart
// ----------------------------------------

function renderIncomeExpensesChart(months) {
    const canvas = document.getElementById(
        "income-expenses-chart"
    );

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: months.map(item => item.month),
            datasets: [
                {
                    label: "Income",
                    data: months.map(item => item.total_income),
                    backgroundColor: "#10b981",
                    borderRadius: 5
                },
                {
                    label: "Expenses",
                    data: months.map(item => item.total_expenses),
                    backgroundColor: "#94a3b8",
                    borderRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: context =>
                            `${context.dataset.label}: ${formatInsightsCurrency(context.parsed.y)
                            }`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}


// ----------------------------------------
// Monthly Net Cash Flow Chart
// ----------------------------------------

function renderNetCashFlowChart(months) {
    const canvas = document.getElementById(
        "net-cash-flow-chart"
    );

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    new Chart(canvas, {
        type: "bar",
        data: {
            labels: months.map(item => item.month),
            datasets: [
                {
                    label: "Net Cash Flow",
                    data: months.map(item => item.net_cash_flow),
                    backgroundColor: months.map(item =>
                        item.net_cash_flow >= 0
                            ? "#10b981"
                            : "#ef4444"
                    ),
                    borderRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: context =>
                            `Net Cash Flow: ${formatInsightsCurrency(context.parsed.y)
                            }`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// ----------------------------------------
// Initialize insights page
// ----------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    loadFinancialInsights();
});
