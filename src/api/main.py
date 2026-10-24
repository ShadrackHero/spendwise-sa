from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg import Error as DatabaseError

from src.database.connection import get_connection


# ----------------------------------------
# 1. Create FastAPI application
# ----------------------------------------

app = FastAPI(
    title="SpendWise SA API",
    description="Personal Finance Analytics Backend",
    version="1.0.0"
)


# ----------------------------------------
# 2. Configure CORS
# ----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"]
)


# ----------------------------------------
# 3. API endpoints
# ----------------------------------------

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
                    "categories_used": result[3]
                }

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable."
        )

# ----------------------------------------
# 4. Financial summary
# ----------------------------------------

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
                    "classified_expenses": float(result[5])
                }

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable."
        )

# ----------------------------------------
# 5. Spending by category
# ----------------------------------------

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
                            "total_spending": float(row[2])
                        }
                        for row in results
                    ]
                }

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable."
        )

# ----------------------------------------
# 6. Monthly spending trends
# ----------------------------------------

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
                            "total_spending": float(row[2])
                        }
                        for row in results
                    ]
                }

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable."
        )

# ----------------------------------------
# 7. Monthly income vs expenses
# ----------------------------------------

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
                            "net": float(row[1] - row[2])
                        }
                        for row in results
                    ]
                }

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable."
        )


# ----------------------------------------
# 8. Recent transactions
# ----------------------------------------

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
                                row[0].isoformat()
                                if row[0] is not None
                                else None
                            ),
                            "category": (
                                row[1]
                                if row[1] is not None
                                else "Uncategorized"
                            ),
                            "amount": (
                                float(row[2])
                                if row[2] is not None
                                else None
                            ),
                            "cash_flow_class": row[3],
                            "review_required": row[4]
                        }
                        for row in results
                    ]
                }

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable."
        )


# ----------------------------------------
# 9. Transactions management
# ----------------------------------------

from fastapi import Query


@app.get("/api/transactions")
def get_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str = "",
    transaction_type: str = "",
    review_only: bool = False
):
    try:
        conditions = []
        parameters = []

        if search.strip():
            conditions.append(
                "COALESCE(c.category_name, '') ILIKE %s"
            )
            parameters.append(f"%{search.strip()}%")

        if transaction_type:
            conditions.append("t.cash_flow_class = %s")
            parameters.append(transaction_type)

        if review_only:
            conditions.append("t.review_required = TRUE")

        where_clause = (
            "WHERE " + " AND ".join(conditions)
            if conditions else ""
        )

        offset = (page - 1) * page_size

        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM transactions t
                    LEFT JOIN categories c
                        ON t.category_id = c.category_id
                    {where_clause}
                    """,
                    parameters
                )

                total = cursor.fetchone()[0]

                cursor.execute(
                    f"""
                    SELECT
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
                        t.category_id

                    LIMIT %s OFFSET %s
                    """,
                    parameters + [page_size, offset]
                )

                rows = cursor.fetchall()

                transactions = [
                    {
                        "transaction_date": (
                            row[0].isoformat()
                            if row[0] is not None else None
                        ),
                        "category": row[1] or "Uncategorized",
                        "amount": (
                            float(row[2])
                            if row[2] is not None else None
                        ),
                        "cash_flow_class": row[3],
                        "review_required": row[4]
                    }
                    for row in rows
                ]

                return {
                    "page": page,
                    "page_size": page_size,
                    "total": total,
                    "total_pages": (
                        (total + page_size - 1) // page_size
                    ),
                    "transactions": transactions
                }

    except DatabaseError:
        raise HTTPException(
            status_code=503,
            detail="Database temporarily unavailable."
        )
