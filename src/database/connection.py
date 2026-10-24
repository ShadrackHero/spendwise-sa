
from pathlib import Path
import os

import psycopg
from dotenv import load_dotenv

# ----------------------------------------
# 1. Load environment variables
# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


# ----------------------------------------
# 2. Create database connection
# ----------------------------------------

def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5
    )


# ----------------------------------------
# 3. Test database connection
# ----------------------------------------

if __name__ == "__main__":

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:

                cursor.execute(
                    "SELECT current_database(), current_user;"
                )

                database, user = cursor.fetchone()

                print("=" * 45)
                print("SPENDWISE SA - DATABASE CONNECTION")
                print("=" * 45)
                print("Database:", database)
                print("Connected user:", user)
                print("Connection successful!")

    except psycopg.Error as error:
        print("Database connection failed.")
        print("Error type:", type(error).__name__)

        # Identify common connection problems
        message = str(error).lower()

        if "password authentication failed" in message:
            print("Cause: Incorrect username or password.")

        elif "connection refused" in message:
            print("Cause: PostgreSQL server is not accepting connections.")

        elif "could not translate host name" in message:
            print("Cause: Invalid database hostname.")

        elif "does not exist" in message:
            print("Cause: Database or PostgreSQL role does not exist.")

        elif "no password supplied" in message:
            print("Cause: Database password is missing.")

        else:
            print("Cause: Unidentified connection error.")
