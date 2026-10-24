
from connection import get_connection

print("=" * 55)
print("SPENDWISE SA - DATABASE VERIFICATION")
print("=" * 55)

with get_connection() as conn:
    with conn.cursor() as cursor:

        # 1. Count imported records
        cursor.execute("""
            SELECT COUNT(*)
            FROM transactions;
        """)
        total = cursor.fetchone()[0]

        # 2. Check missing financial values
        cursor.execute("""
            SELECT
                COUNT(*) FILTER (
                    WHERE balance IS NULL
                ),
                COUNT(*) FILTER (
                    WHERE transaction_amount IS NULL
                ),
                COUNT(*) FILTER (
                    WHERE cash_flow IS NULL
                )
            FROM transactions;
        """)
        missing_balance, missing_amount, missing_cash_flow = (
            cursor.fetchone()
        )

        # 3. Verify category relationships
        cursor.execute("""
            SELECT COUNT(*)
            FROM transactions
            WHERE category_id IS NULL;
        """)
        missing_categories = cursor.fetchone()[0]

        # 4. Verify financial reconciliation
        cursor.execute("""
            SELECT
                COALESCE(SUM(money_in), 0)
                + COALESCE(SUM(money_out), 0)
                + COALESCE(SUM(fee), 0)
                - COALESCE(SUM(cash_flow), 0)
            FROM transactions;
        """)
        reconciliation_difference = cursor.fetchone()[0]

        # 5. Count review-required records
        cursor.execute("""
            SELECT COUNT(*)
            FROM transactions
            WHERE review_required = TRUE;
        """)
        review_count = cursor.fetchone()[0]

print("\nTotal transactions:", total)
print("Missing balances:", missing_balance)
print("Missing amounts:", missing_amount)
print("Missing cash-flow values:", missing_cash_flow)
print("Missing category relationships:", missing_categories)
print("Financial reconciliation difference:", reconciliation_difference)
print("Review-required records:", review_count)

print("\nDatabase verification completed!")
