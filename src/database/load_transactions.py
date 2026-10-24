
from pathlib import Path
from datetime import datetime
import pandas as pd

from connection import get_connection

# ----------------------------------------
# 1. File paths
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "data/processed/transactions_categorized.csv"
)

# ----------------------------------------
# 2. Load and validate data
# ----------------------------------------

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=["posting_date", "transaction_date"]
)

if df.empty:
    raise ValueError("Transaction file is empty.")

if df["nr"].isna().any() or not df["nr"].is_unique:
    raise ValueError("Invalid or duplicate source row IDs.")

if df["spendwise_category"].isna().any():
    raise ValueError("Unmapped SpendWise categories found.")

# ----------------------------------------
# 3. Determine statement period
# ----------------------------------------

period_start = df["transaction_date"].min().date()
period_end = df["transaction_date"].max().date()

# Use a non-sensitive statement label
statement_label = "Capitec Historical Import"

# ----------------------------------------
# 4. Convert pandas values to SQL values
# ----------------------------------------

def sql_value(value):
    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if hasattr(value, "item"):
        return value.item()

    return value

# ----------------------------------------
# 5. Connect to PostgreSQL
# ----------------------------------------

print("=" * 55)
print("SPENDWISE SA - TRANSACTION IMPORT")
print("=" * 55)

print("CSV transactions:", len(df))

with get_connection() as conn:
    with conn.cursor() as cursor:

        # Retrieve existing categories
        cursor.execute(
            "SELECT category_id, category_name FROM categories;"
        )

        category_lookup = {
            name: category_id
            for category_id, name in cursor.fetchall()
        }

        missing_categories = (
            set(df["spendwise_category"])
            - set(category_lookup)
        )

        if missing_categories:
            raise ValueError(
                f"Categories missing from database: {missing_categories}"
            )

        # ----------------------------------------
        # 6. Register statement
        # ----------------------------------------

        cursor.execute(
            """
            SELECT statement_id
            FROM statements
            WHERE bank_name = %s
              AND account_label = %s
              AND period_start = %s
              AND period_end = %s
            ORDER BY statement_id
            LIMIT 1;
            """,
            (
                "Capitec",
                statement_label,
                period_start,
                period_end
            )
        )

        existing = cursor.fetchone()

        if existing:
            statement_id = existing[0]
        else:
            cursor.execute(
                """
                INSERT INTO statements (
                    bank_name,
                    account_label,
                    period_start,
                    period_end
                )
                VALUES (%s, %s, %s, %s)
                RETURNING statement_id;
                """,
                (
                    "Capitec",
                    statement_label,
                    period_start,
                    period_end
                )
            )

            statement_id = cursor.fetchone()[0]

        # ----------------------------------------
        # 7. Import transactions
        # ----------------------------------------

        inserted = 0
        skipped = 0

        for row in df.itertuples(index=False):

            cursor.execute(
                """
                INSERT INTO transactions (
                    statement_id,
                    category_id,
                    source_row_nr,
                    posting_date,
                    transaction_date,
                    description,
                    original_description,
                    parent_category,
                    bank_category,
                    transaction_type,
                    cash_flow_class,
                    money_in,
                    money_out,
                    fee,
                    balance,
                    transaction_amount,
                    cash_flow,
                    posting_delay_days,
                    review_required
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                ON CONFLICT (
                    statement_id,
                    source_row_nr
                )
                DO NOTHING;
                """,
                (
                    statement_id,
                    category_lookup[row.spendwise_category],
                    sql_value(row.nr),
                    sql_value(row.posting_date),
                    sql_value(row.transaction_date),
                    sql_value(row.description),
                    sql_value(row.original_description),
                    sql_value(row.parent_category),
                    sql_value(row.category),
                    sql_value(row.transaction_type),
                    sql_value(row.cash_flow_class),
                    sql_value(row.money_in),
                    sql_value(row.money_out),
                    sql_value(row.fee),
                    sql_value(row.balance),
                    sql_value(row.transaction_amount),
                    sql_value(row.cash_flow),
                    sql_value(row.posting_delay_days),
                    sql_value(row.review_required)
                )
            )

            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

        # ----------------------------------------
        # 8. Verify import
        # ----------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM transactions
            WHERE statement_id = %s;
            """,
            (statement_id,)
        )

        total = cursor.fetchone()[0]

print("\nNew transactions inserted:", inserted)
print("Existing transactions skipped:", skipped)
print("Transactions linked to statement:", total)
print("Import completed successfully!")
