
# ----------------------------------------
# SPENDWISE SA
# CHAPTER 15 - STEP 15.1
# Inspect Transaction Date Range
# ----------------------------------------

from src.database.connection import get_connection


def check_transaction_dates():

    query = """
        SELECT
            COUNT(*) AS total_transactions,
            MIN(posting_date) AS earliest_transaction,
            MAX(posting_date) AS latest_transaction,
            COUNT(*) FILTER (
                WHERE posting_date IS NULL
            ) AS missing_posting_dates
        FROM transactions;
    """

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()

                print("\nSPENDWISE SA - TRANSACTION DATE ANALYSIS")
                print("----------------------------------------")
                print(f"Total Transactions: {result[0]}")
                print(f"Earliest Transaction: {result[1]}")
                print(f"Latest Transaction: {result[2]}")
                print(f"Missing Posting Dates: {result[3]}")
                print("----------------------------------------")

    except Exception as error:
        print(f"Database error: {error}")


if __name__ == "__main__":
    check_transaction_dates()