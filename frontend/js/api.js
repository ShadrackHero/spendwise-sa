
const API_BASE_URL = "http://127.0.0.1:8000";

async function fetchAPI(endpoint) {
    const response = await fetch(
        `${API_BASE_URL}${endpoint}`
    );

    if (!response.ok) {
        throw new Error(
            `API request failed: ${response.status}`
        );
    }

    return await response.json();
}

async function getTransactionSummary() {
    return await fetchAPI("/api/summary");
}

async function getFinancialSummary() {
    return await fetchAPI("/api/financial-summary");
}

async function getSpendingByCategory() {
    return await fetchAPI("/api/spending-by-category");
}

async function getMonthlyCashFlow() {
    return await fetchAPI("/api/monthly-cash-flow");
}

async function getMonthlySpending() {
    return await fetchAPI("/api/monthly-spending");
}


 // ----------------------------------------
 // Get recent transactions
 // ----------------------------------------

 async function getRecentTransactions() {
     const response = await fetch(
         "http://127.0.0.1:8000/api/recent-transactions"
     );

     if (!response.ok) {
         throw new Error(
             `Failed to load recent transactions: ${response.status}`
         );
     }

     return await response.json();
 }


// ----------------------------------------
// Transactions management API
// ----------------------------------------

async function getTransactions(filters = {}) {

    const params = new URLSearchParams({
        page: filters.page || 1,
        page_size: filters.pageSize || 20,
        search: filters.search || "",
        transaction_type: filters.type || "",
        review_only: filters.reviewOnly || false
    });

    const response = await fetch(
        `http://127.0.0.1:8000/api/transactions?${params}`
    );

    if (!response.ok) {
        throw new Error(
            `Transactions request failed: ${response.status}`
        );
    }

    return await response.json();
}
