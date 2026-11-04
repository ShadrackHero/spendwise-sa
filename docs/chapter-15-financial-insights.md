# Chapter 15 — Financial Insights & Analytics

**Project:** SpendWise SA  
**Technology:** Python, FastAPI, PostgreSQL, JavaScript, HTML, CSS, Chart.js  
**Status:** Implementation and integration testing completed  
**Date:** 4 November 2026

## 1. Chapter Overview

Chapter 15 introduces monthly financial analytics to SpendWise SA.

The objective was to transform existing transaction records into meaningful financial information that users can explore through an interactive Insights dashboard.

The implementation connects PostgreSQL financial data to FastAPI endpoints and displays the results through a dedicated frontend page.

## 2. Transaction Date Investigation

Before building financial analytics, we investigated the available transaction dates.

A Python diagnostic script was created:

`scripts/check_transaction_dates.py`

The script queries PostgreSQL to identify the total number of transactions, earliest and latest posting dates, and missing posting dates.

**Verified results:**

| Metric | Result |
|---|---|
| Total transactions | 1,464 |
| Earliest posting date | 23 October 2025 |
| Latest posting date | 19 October 2026 |
| Missing posting dates | 0 |
| Reporting months | 13 |

This confirmed that the database contained sufficient dated transactions for monthly analysis.

## 3. Financial Classification Investigation

The initial monthly analysis revealed unusually low classified income.

Further investigation showed that several genuine employment payments were classified as `Review` rather than `Income`.

We examined transaction descriptions, amounts, categories, and cash-flow classifications to identify the affected records.

### Salary Reclassification

Eight salary transactions were confirmed as genuine employment income.

The following corrections were applied:

- Category changed to `Employment Income` (category ID 6).
- Cash-flow classification changed from `Review` to `Income`.
- Existing transaction amounts were preserved.

**Total reclassified employment income: R117,452.93**

The update was performed using guarded SQL conditions and verified before committing the database transaction.

## 4. Monthly Financial Calculations

Monthly analytics were calculated using the `transactions` table.

The calculations follow three rules:

**Classified income:** Sum of positive cash-flow amounts classified as `Income`.

**Classified expenses:** Sum of the absolute values of negative cash-flow amounts classified as `Expense`.

**Net classified cash flow:** Classified income minus classified expenses.

Transactions classified as `Review` or `Transfer / Review` are excluded from these calculations.

### Verified Financial Results

| Indicator | Amount |
|---|---:|
| Total classified income | R117,462.79 |
| Total classified expenses | R75,035.69 |
| Net classified cash flow | R42,427.10 |
| Months analyzed | 13 |

These results cover October 2025 through October 2026.

**Important limitation:** These figures do not necessarily represent the full bank-account cash flow or actual savings because unresolved transactions remain excluded.

## 5. Monthly Financial Analytics API

A new FastAPI endpoint was implemented:

`GET /api/analytics/monthly`

**Backend file:** `src/api/main.py`

The endpoint:

1. Establishes a PostgreSQL connection.
2. Groups transactions by posting month.
3. Calculates classified income and expenses.
4. Calculates net classified cash flow.
5. Returns monthly financial results in JSON format.
6. Handles database errors with an HTTP 503 response.

The endpoint is read-only and does not modify financial transactions.

## 6. Insights Frontend

A new frontend page was created:

`frontend/insights.html`

The page follows the existing SpendWise SA design system, including the dark sidebar, navigation links, summary cards, and content panels.

Its JavaScript functionality is implemented in:

`frontend/js/insights.js`

The page retrieves monthly analytics from FastAPI and displays:

- Total classified income
- Total classified expenses
- Net classified cash flow
- Number of reporting months
- Monthly income versus expenses chart
- Monthly net cash flow chart
- Monthly financial performance table

Chart.js is used to render the financial visualizations.

## 7. Navigation Integration

The Insights page was connected to the existing sidebar navigation.

The application now includes four connected pages:

1. Dashboard
2. Transactions
3. Categories
4. Insights

The active page is highlighted through the existing CSS navigation classes.

## 8. Integration Testing

The monthly analytics endpoint was tested using Python's `requests` library.

**Verified test results:**

| Test | Result |
|---|---|
| Monthly API HTTP response | 200 |
| Reporting months | 13 |
| Monthly records | 13 |
| Income total | R117,462.79 |
| Expenses total | R75,035.69 |
| Net classified cash flow | R42,427.10 |
| Dashboard income consistency | Passed |
| Dashboard expense consistency | Passed |
| Sidebar navigation | Passed |
| Insights charts | Passed |

The backend calculations, API responses, and frontend financial displays were verified to be consistent.

## 9. Files Created or Modified

| File | Purpose |
|---|---|
| `src/api/main.py` | Monthly analytics endpoint |
| `frontend/insights.html` | Insights page layout |
| `frontend/js/insights.js` | Financial data loading and charts |
| `frontend/css/style.css` | Insights chart styling |
| `frontend/index.html` | Insights navigation |
| `frontend/categories.html` | Insights navigation |
| `scripts/check_transaction_dates.py` | Transaction date diagnostic script |

## 10. Outstanding Work

Although the financial analytics implementation is functioning, several opportunities remain for future improvements.

These include reviewing unresolved financial classifications, expanding income categorization, adding date-range filters, and strengthening automated tests.

The existing classified financial totals should not be interpreted as a complete financial position until outstanding transaction classifications have been reviewed.

## 11. Chapter Conclusion

Chapter 15 established the first complete monthly financial analytics workflow in SpendWise SA.

The application can now retrieve transaction information from PostgreSQL, calculate monthly financial performance through FastAPI, and display the results using interactive frontend charts and tables.

The implementation provides a foundation for more advanced personal-finance analytics in future chapters.