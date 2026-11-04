# ========================================
# SPENDWISE SA - FASTAPI BACKEND
# ========================================

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from psycopg import Error as DatabaseError

from src.database.connection import get_connection

# ========================================
# 1. REQUEST MODELS
# ========================================


class TransactionReviewUpdate(BaseModel):
    review_required: bool


# ----------------------------------------
# Transaction category update model
# ----------------------------------------


class TransactionCategoryUpdate(BaseModel):
    category_id: int


# ========================================
# 2. CREATE FASTAPI APPLICATION
# ========================================

app = FastAPI(
    title="SpendWise SA API",
    description="Personal Finance Analytics Backend",
    version="1.0.0",
)


# ========================================
# 3. CONFIGURE CORS
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=False,
    allow_methods=["GET", "PATCH"],
    allow_headers=["*"],
)


# ========================================
# 4. HOMEPAGE
# ========================================


@app.get("/")
def home():
    return {
        "application": "SpendWise SA",
        "status": "running",
        "message": "Welcome to SpendWise SA API",
    }


# ========================================
# 5. DASHBOARD SUMMARY
# ========================================


@app.get("/api/summary")
def get_summary():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        COUNT(*) AS total_transactions,

                        COUNT(*) FILTER (
                            WHERE review_required = TRUE
                        ) AS review_required,

                        COUNT(*) FILTER (
                            WHERE cash_flow IS NULL
                        ) AS missing_cash_flow,

                        COUNT(DISTINCT category_id)
                            AS categories_used

                    FROM transactions;
                """)

                result = cursor.fetchone()

                return {
                    "total_transactions": result[0],
                    "review_required": result[1],
                    "missing_cash_flow": result[2],
                    "categories_used": result[3],
                }

    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ========================================
# 6. FINANCIAL SUMMARY
# ========================================


@app.get("/api/financial-summary")
def get_financial_summary():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        COUNT(*) FILTER (
                            WHERE cash_flow_class = 'Income'
                        ) AS income_records,

                        COUNT(*) FILTER (
                            WHERE cash_flow_class = 'Expense'
                        ) AS expense_records,

                        COUNT(*) FILTER (
                            WHERE cash_flow_class = 'Transfer / Review'
                        ) AS transfer_review_records,

                        COUNT(*) FILTER (
                            WHERE cash_flow_class = 'Review'
                        ) AS review_records,

                        COALESCE(
                            SUM(cash_flow) FILTER (
                                WHERE cash_flow_class = 'Income'
                            ), 0
                        ) AS classified_income,

                        COALESCE(
                            SUM(-cash_flow) FILTER (
                                WHERE cash_flow_class = 'Expense'
                                  AND cash_flow < 0
                            ), 0
                        ) AS classified_expenses

                    FROM transactions;
                """)

                result = cursor.fetchone()

                return {
                    "income_records": result[0],
                    "expense_records": result[1],
                    "transfer_review_records": result[2],
                    "review_records": result[3],
                    "classified_income": float(result[4]),
                    "classified_expenses": float(result[5]),
                }

    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ========================================
# 7. SPENDING BY CATEGORY
# ========================================


@app.get("/api/spending-by-category")
def get_spending_by_category():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        c.category_name,

                        COUNT(*) AS transaction_count,

                        COALESCE(
                            SUM(-t.cash_flow), 0
                        ) AS total_spending

                    FROM transactions t

                    JOIN categories c
                        ON t.category_id = c.category_id

                    WHERE t.cash_flow_class = 'Expense'
                      AND t.cash_flow < 0

                    GROUP BY c.category_name

                    ORDER BY total_spending DESC;
                """)

                results = cursor.fetchall()

                return {
                    "categories": [
                        {
                            "category": row[0],
                            "transaction_count": row[1],
                            "total_spending": float(row[2]),
                        }
                        for row in results
                    ]
                }

    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ========================================
# 8. MONTHLY SPENDING TRENDS
# ========================================


@app.get("/api/monthly-spending")
def get_monthly_spending():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        TO_CHAR(
                            DATE_TRUNC('month', transaction_date),
                            'YYYY-MM'
                        ) AS month,

                        COUNT(*) AS transaction_count,

                        COALESCE(
                            SUM(-cash_flow), 0
                        ) AS total_spending

                    FROM transactions

                    WHERE cash_flow_class = 'Expense'
                      AND cash_flow < 0
                      AND transaction_date IS NOT NULL

                    GROUP BY DATE_TRUNC(
                        'month', transaction_date
                    )

                    ORDER BY DATE_TRUNC(
                        'month', transaction_date
                    );
                """)

                results = cursor.fetchall()

                return {
                    "monthly_spending": [
                        {
                            "month": row[0],
                            "transaction_count": row[1],
                            "total_spending": float(row[2]),
                        }
                        for row in results
                    ]
                }

    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ========================================
# 9. MONTHLY INCOME VS EXPENSES
# ========================================


@app.get("/api/monthly-cash-flow")
def get_monthly_cash_flow():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        TO_CHAR(
                            DATE_TRUNC('month', transaction_date),
                            'YYYY-MM'
                        ) AS month,

                        COALESCE(
                            SUM(cash_flow) FILTER (
                                WHERE cash_flow_class = 'Income'
                                  AND cash_flow > 0
                            ), 0
                        ) AS income,

                        COALESCE(
                            SUM(-cash_flow) FILTER (
                                WHERE cash_flow_class = 'Expense'
                                  AND cash_flow < 0
                            ), 0
                        ) AS expenses

                    FROM transactions

                    WHERE transaction_date IS NOT NULL

                    GROUP BY DATE_TRUNC(
                        'month', transaction_date
                    )

                    ORDER BY DATE_TRUNC(
                        'month', transaction_date
                    );
                """)

                results = cursor.fetchall()

                return {
                    "monthly_cash_flow": [
                        {
                            "month": row[0],
                            "income": float(row[1]),
                            "expenses": float(row[2]),
                            "net": float(row[1] - row[2]),
                        }
                        for row in results
                    ]
                }

    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ========================================
# 10. RECENT TRANSACTIONS
# ========================================


@app.get("/api/recent-transactions")
def get_recent_transactions():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        t.transaction_date,
                        c.category_name,
                        t.cash_flow,
                        t.cash_flow_class,
                        t.review_required

                    FROM transactions t

                    LEFT JOIN categories c
                        ON t.category_id = c.category_id

                    ORDER BY
                        t.transaction_date DESC NULLS LAST

                    LIMIT 10;
                """)

                results = cursor.fetchall()

                return {
                    "recent_transactions": [
                        {
                            "transaction_date": (
                                row[0].isoformat() if row[0] is not None else None
                            ),
                            "category": (
                                row[1] if row[1] is not None else "Uncategorized"
                            ),
                            "amount": (float(row[2]) if row[2] is not None else None),
                            "cash_flow_class": row[3],
                            "review_required": row[4],
                        }
                        for row in results
                    ]
                }

    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ========================================
# 11. TRANSACTIONS MANAGEMENT
# ========================================


@app.get("/api/transactions")
def get_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str = "",
    transaction_type: str = "",
    review_only: bool = False,
):

    try:
        conditions = []
        parameters = []

        # Search by category
        if search.strip():
            conditions.append("COALESCE(c.category_name, '') ILIKE %s")
            parameters.append(f"%{search.strip()}%")

        # Filter by transaction type
        if transaction_type:
            conditions.append("t.cash_flow_class = %s")
            parameters.append(transaction_type)

        # Filter transactions requiring review
        if review_only:
            conditions.append("t.review_required = TRUE")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        offset = (page - 1) * page_size

        with get_connection() as conn:
            with conn.cursor() as cursor:

                # Count matching transactions
                cursor.execute(
                    f"""
                    SELECT COUNT(*)

                    FROM transactions t

                    LEFT JOIN categories c
                        ON t.category_id = c.category_id

                    {where_clause}
                    """,
                    parameters,
                )

                total = cursor.fetchone()[0]

                # Retrieve paginated transactions
                cursor.execute(
                    f"""
                    SELECT
                        t.transaction_id,
                        t.transaction_date,
                        c.category_name,
                        t.cash_flow,
                        t.cash_flow_class,
                        t.review_required

                    FROM transactions t

                    LEFT JOIN categories c
                        ON t.category_id = c.category_id

                    {where_clause}

                    ORDER BY
                        t.transaction_date DESC NULLS LAST,
                        t.transaction_id DESC

                    LIMIT %s OFFSET %s
                    """,
                    parameters + [page_size, offset],
                )

                rows = cursor.fetchall()

                transactions = [
                    {
                        "transaction_id": row[0],
                        "transaction_date": (
                            row[1].isoformat() if row[1] is not None else None
                        ),
                        "category": (row[2] if row[2] is not None else "Uncategorized"),
                        "amount": (float(row[3]) if row[3] is not None else None),
                        "cash_flow_class": row[4],
                        "review_required": row[5],
                    }
                    for row in rows
                ]

                return {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": ((total + page_size - 1) // page_size),
                    "transactions": transactions,
                }

    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ========================================
# 12. INDIVIDUAL TRANSACTION DETAILS
# ========================================


@app.get("/api/transactions/{transaction_id}")
def get_transaction_details(transaction_id: int):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        t.transaction_id,
                        t.statement_id,
                        t.source_row_nr,
                        t.transaction_date,
                        t.posting_date,
                        t.description,
                        t.original_description,
                        t.parent_category,
                        t.bank_category,
                        t.transaction_type,
                        t.cash_flow_class,
                        t.money_in,
                        t.money_out,
                        t.fee,
                        t.balance,
                        t.transaction_amount,
                        t.cash_flow,
                        t.posting_delay_days,
                        t.review_required,
                        t.created_at,
                        t.category_id,
                        c.category_name

                    FROM transactions t

                    LEFT JOIN categories c
                        ON t.category_id = c.category_id

                    WHERE t.transaction_id = %s;
                    """,
                    (transaction_id,),
                )

                row = cursor.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404, detail="Transaction not found."
                    )

                return {
                    "transaction_id": row[0],
                    "statement_id": row[1],
                    "source_row_nr": row[2],
                    "transaction_date": (
                        row[3].isoformat() if row[3] is not None else None
                    ),
                    "posting_date": (
                        row[4].isoformat() if row[4] is not None else None
                    ),
                    "description": row[5],
                    "original_description": row[6],
                    "parent_category": row[7],
                    "bank_category": row[8],
                    "transaction_type": row[9],
                    "cash_flow_class": row[10],
                    "money_in": (float(row[11]) if row[11] is not None else None),
                    "money_out": (float(row[12]) if row[12] is not None else None),
                    "fee": (float(row[13]) if row[13] is not None else None),
                    "balance": (float(row[14]) if row[14] is not None else None),
                    "transaction_amount": (
                        float(row[15]) if row[15] is not None else None
                    ),
                    "cash_flow": (float(row[16]) if row[16] is not None else None),
                    "posting_delay_days": row[17],
                    "review_required": row[18],
                    "created_at": (
                        row[19].isoformat() if row[19] is not None else None
                    ),
                    "category_id": row[20],
                    "category": (row[21] if row[21] is not None else "Uncategorized"),
                }

    except DatabaseError:
        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ========================================
# 13. UPDATE TRANSACTION REVIEW STATUS
# ========================================


@app.patch("/api/transactions/{transaction_id}/review")
def update_transaction_review(transaction_id: int, payload: TransactionReviewUpdate):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    UPDATE transactions

                    SET review_required = %s

                    WHERE transaction_id = %s

                    RETURNING
                        transaction_id,
                        review_required;
                    """,
                    (payload.review_required, transaction_id),
                )

                result = cursor.fetchone()

                if result is None:
                    raise HTTPException(
                        status_code=404, detail="Transaction not found."
                    )

                conn.commit()

                return {
                    "transaction_id": result[0],
                    "review_required": result[1],
                    "message": ("Transaction review status " "updated successfully."),
                }

    except HTTPException:
        raise

    except DatabaseError as error:

        print("Database error:", error)

        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")


# ========================================
# 14. GET ALL TRANSACTION CATEGORIES
# ========================================


@app.get("/api/categories")
def get_categories():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        category_id,
                        category_name,
                        description

                    FROM categories

                    ORDER BY category_name ASC;
                """)

                rows = cursor.fetchall()

                return {
                    "total_categories": len(rows),
                    "categories": [
                        {
                            "category_id": row[0],
                            "category_name": row[1],
                            "description": row[2],
                        }
                        for row in rows
                    ],
                }

    except DatabaseError as error:

        print("Database error:", error)

        raise HTTPException(status_code=503, detail="Unable to retrieve categories.")


# ========================================
# 15. UPDATE TRANSACTION CATEGORY
# ========================================


@app.patch("/api/transactions/{transaction_id}/category")
def update_transaction_category(
    transaction_id: int, payload: TransactionCategoryUpdate
):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                # Check whether the selected category exists
                cursor.execute(
                    """
                    SELECT category_id, category_name
                    FROM categories
                    WHERE category_id = %s;
                    """,
                    (payload.category_id,),
                )

                category = cursor.fetchone()

                if category is None:
                    raise HTTPException(status_code=404, detail="Category not found.")

                # Update the transaction category
                cursor.execute(
                    """
                    UPDATE transactions
                    SET category_id = %s
                    WHERE transaction_id = %s
                    RETURNING transaction_id, category_id;
                    """,
                    (payload.category_id, transaction_id),
                )

                result = cursor.fetchone()

                if result is None:
                    raise HTTPException(
                        status_code=404, detail="Transaction not found."
                    )

                conn.commit()

                return {
                    "transaction_id": result[0],
                    "category_id": result[1],
                    "category_name": category[1],
                    "message": "Transaction category updated successfully.",
                }

    except HTTPException:
        raise

    except DatabaseError as error:

        print("Database error:", error)

        raise HTTPException(status_code=503, detail="Database temporarily unavailable.")

# ========================================
# CHAPTER 14 - CATEGORIES SUMMARY API
# ========================================

@app.get("/api/categories/summary")
def get_categories_summary():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                # ----------------------------------------
                # 1. Count available categories
                # ----------------------------------------

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM categories;
                """)

                total_categories = cursor.fetchone()[0]

                # ----------------------------------------
                # 2. Calculate transaction statistics
                # ----------------------------------------

                cursor.execute("""
                    SELECT

                        COUNT(*) AS total_transactions,

                        COUNT(*) FILTER (
                            WHERE t.category_id IS NOT NULL
                              AND (
                                  c.category_name IS NULL
                                  OR c.category_name <> 'Uncategorized'
                              )
                        ) AS categorized_transactions,

                        COUNT(*) FILTER (
                            WHERE t.category_id IS NULL
                               OR c.category_name = 'Uncategorized'
                        ) AS uncategorized_transactions,

                        COALESCE(
                            SUM(-t.cash_flow) FILTER (
                                WHERE t.cash_flow_class = 'Expense'
                                  AND t.cash_flow < 0
                            ), 0
                        ) AS total_expenses

                    FROM transactions t

                    LEFT JOIN categories c
                        ON t.category_id = c.category_id;
                """)

                result = cursor.fetchone()

                return {
                    "total_categories": total_categories,
                    "total_transactions": result[0],
                    "categorized_transactions": result[1],
                    "uncategorized_transactions": result[2],
                    "total_expenses": float(result[3])
                }

    except DatabaseError as error:

        print("Categories summary database error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve categories summary."
        )


# ========================================
# CHAPTER 14 - CATEGORIES TABLE API
# ========================================

@app.get("/api/categories/statistics")
def get_categories_statistics():

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    WITH category_stats AS (
                        SELECT
                            c.category_id,
                            c.category_name,

                            COUNT(t.transaction_id)
                                AS transaction_count,

                            COALESCE(
                                SUM(-t.cash_flow) FILTER (
                                    WHERE t.cash_flow_class = 'Expense'
                                      AND t.cash_flow < 0
                                ), 0
                            ) AS total_expenses

                        FROM categories c

                        LEFT JOIN transactions t
                            ON c.category_id = t.category_id

                        GROUP BY
                            c.category_id,
                            c.category_name
                    )

                    SELECT
                        category_id,
                        category_name,
                        transaction_count,
                        total_expenses,

                        CASE
                            WHEN SUM(total_expenses) OVER () > 0
                            THEN ROUND(
                                total_expenses * 100.0
                                / SUM(total_expenses) OVER (), 2
                            )
                            ELSE 0
                        END AS expense_percentage

                    FROM category_stats

                    ORDER BY
                        total_expenses DESC,
                        category_name ASC;
                """)

                rows = cursor.fetchall()

                categories = []

                for row in rows:
                    categories.append({
                        "category_id": row[0],
                        "category_name": row[1],
                        "transaction_count": row[2],
                        "total_expenses": float(row[3]),
                        "expense_percentage": float(row[4])
                    })

                return {
                    "total_categories": len(categories),
                    "categories": categories
                }

    except DatabaseError as error:

        print("Categories statistics database error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve category statistics."
        )


# ========================================
# CHAPTER 14 - CATEGORY DETAILS API
# ========================================

@app.get("/api/categories/{category_id}")
def get_category_details(category_id: int):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        c.category_id,
                        c.category_name,
                        c.description,

                        COUNT(t.transaction_id)
                            AS transaction_count,

                        COALESCE(
                            SUM(-t.cash_flow) FILTER (
                                WHERE t.cash_flow_class = 'Expense'
                                  AND t.cash_flow < 0
                            ), 0
                        ) AS total_expenses,

                        COALESCE(
                            SUM(t.cash_flow) FILTER (
                                WHERE t.cash_flow_class = 'Income'
                            ), 0
                        ) AS total_income

                    FROM categories c

                    LEFT JOIN transactions t
                        ON c.category_id = t.category_id

                    WHERE c.category_id = %s

                    GROUP BY
                        c.category_id,
                        c.category_name,
                        c.description;
                """, (category_id,))

                result = cursor.fetchone()

                if result is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Category not found."
                    )

                return {
                    "category_id": result[0],
                    "category_name": result[1],
                    "description": result[2],
                    "transaction_count": result[3],
                    "total_expenses": float(result[4]),
                    "total_income": float(result[5])
                }

    except DatabaseError as error:

        print("Category details database error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve category details."
        )
