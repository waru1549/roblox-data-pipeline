
import os
import sys
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import Text, BigInteger, Integer, Float


# ==========================================
# 1. CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

CSV_FILE = BASE_DIR / "roblox_games_data.csv"

DB_HOST = "localhost"
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

SCHEMA_NAME = "raw_data"
TABLE_NAME = "roblox_games_data"

CHUNK_SIZE = 5000


# ==========================================
# 2. DATABASE CONNECTION
# ==========================================

def create_db_engine():

    required = {
        "POSTGRES_DB": DB_NAME,
        "POSTGRES_USER": DB_USER,
        "POSTGRES_PASSWORD": DB_PASSWORD
    }

    missing = [key for key, value in required.items() if not value]

    if missing:
        raise ValueError(
            f"Missing environment variables: {missing}"
        )

    connection_url = (
        f"postgresql+psycopg2://"
        f"{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    engine = create_engine(
        connection_url,
        pool_pre_ping=True
    )

    return engine


# ==========================================
# 3. CREATE SCHEMA
# ==========================================

def create_schema(engine):

    with engine.begin() as connection:

        connection.execute(
            text(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA_NAME}"')
        )

    print(f"Schema '{SCHEMA_NAME}' is ready.")


# ==========================================
# 4. LOAD CSV
# ==========================================


def load_csv():

    if not CSV_FILE.exists():
        raise FileNotFoundError(
            f"CSV file not found: {CSV_FILE}"
        )

    print("Reading CSV file...")

    df = pd.read_csv(
        CSV_FILE,
        low_memory=False
    )

    # Remove unnecessary CSV index column
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
        print("Removed unnecessary index column.")

    print(f"CSV loaded successfully: {len(df):,} rows")
    print(f"Columns: {len(df.columns)}")

    return df


# ==========================================
# 5. DEFINE DATA TYPES
# ==========================================


def get_dtype_mapping(df):

    dtype_mapping = {}

    for column in df.columns:

        if column in [
            "Active Users",
            "Favorites",
            "gameID"
        ]:
            dtype_mapping[column] = BigInteger()

        elif column == "Server Size":
            dtype_mapping[column] = Integer()

        else:
            dtype_mapping[column] = Text()

    return dtype_mapping


# ==========================================
# 6. INSERT DATA INTO POSTGRESQL
# ==========================================

def insert_data(engine, df):

    dtype_mapping = get_dtype_mapping(df)

    print("Loading data into PostgreSQL...")

    df.to_sql(
        name=TABLE_NAME,
        con=engine,
        schema=SCHEMA_NAME,
        if_exists="replace",
        index=False,
        dtype=dtype_mapping,
        chunksize=CHUNK_SIZE,
        method="multi"
    )

    print("Data insertion completed.")


# ==========================================
# 7. VERIFY DATA
# ==========================================

def verify_data(engine):

    with engine.connect() as connection:

        result = connection.execute(
            text(
                f'SELECT COUNT(*) FROM '
                f'"{SCHEMA_NAME}"."{TABLE_NAME}"'
            )
        )

        row_count = result.scalar_one()

        print("\n========== VERIFICATION ==========")
        print(f"Database: {DB_NAME}")
        print(f"Schema: {SCHEMA_NAME}")
        print(f"Table: {TABLE_NAME}")
        print(f"Total rows: {row_count:,}")
        print("==================================")

        return row_count


# ==========================================
# 8. MAIN PROGRAM
# ==========================================

def main():

    print("======================================")
    print(" ROBLOX GAMES DATA - INGESTION")
    print("======================================")

    try:

        engine = create_db_engine()

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        print("PostgreSQL connection successful.")

        create_schema(engine)

        df = load_csv()

        insert_data(engine, df)

        row_count = verify_data(engine)

        if row_count != len(df):
            raise RuntimeError(
                "Row count mismatch between CSV and PostgreSQL."
            )

        print("\nINGESTION COMPLETED SUCCESSFULLY!")

        engine.dispose()

    except Exception as error:

        print("\nINGESTION FAILED!")
        print(f"Error: {error}")

        sys.exit(1)


if __name__ == "__main__":
    main()
