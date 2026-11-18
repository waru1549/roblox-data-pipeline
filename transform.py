import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ==========================================
# 1. CONFIGURATION
# ==========================================
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DB_HOST = "localhost"
DB_PORT = os.getenv("POSTGRES_PORT", "5433")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

RAW_SCHEMA = "raw_data"
PROD_SCHEMA = "production"
TABLE_NAME = "roblox_games_data"

# ==========================================
# 2. DATABASE CONNECTION
# ==========================================
def create_db_engine():
    connection_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(connection_url, pool_pre_ping=True)

# ==========================================
# 3. HELPER FUNCTIONS FOR CLEANING
# ==========================================
def clean_total_visits(value):
    """แปลง Total Visits จากอักษรย่อเป็นตัวเลข (K=10^3, M=10^6, B=10^9)"""
    if pd.isna(value):
        return 0
        
    val_str = str(value).replace('+', '').strip()
    
    try:
        if 'B' in val_str:
            return int(float(val_str.replace('B', '')) * 1e9)
        elif 'M' in val_str:
            return int(float(val_str.replace('M', '')) * 1e6)
        elif 'K' in val_str:
            return int(float(val_str.replace('K', '')) * 1e3)
        else:
            return int(float(val_str))
    except ValueError:
        return 0

# ==========================================
# 4. TRANSFORM LOGIC
# ==========================================
def transform_data(engine):
    print(f"Reading data from {RAW_SCHEMA}.{TABLE_NAME}...")
    
    # ดึงข้อมูลจาก raw_data
    df = pd.read_sql_table(TABLE_NAME, con=engine, schema=RAW_SCHEMA)
    print(f"Data loaded: {len(df):,} rows")

    print("Cleaning and transforming data...")
    
    # 1. ลบคอลัมน์ที่ไม่จำเป็น (Unnamed: 0, URL)
    cols_to_drop = ["Unnamed: 0", "URL"]
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')

    # 2. จัดการค่าว่าง (Missing Values)
    if "Description" in df.columns:
        df["Description"] = df["Description"].fillna("N/A")

    # 3. แปลงรูปแบบ Date ให้สม่ำเสมอ (Date, Date Created, Last Updated)
    print("Formatting dates...")
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], format='mixed', errors='coerce')
    
    if "Date Created" in df.columns:
        df["Date Created"] = pd.to_datetime(df["Date Created"], format='mixed', errors='coerce')
        
    if "Last Updated" in df.columns:
        df["Last Updated"] = pd.to_datetime(df["Last Updated"], format='mixed', errors='coerce')

    # 4. แปลง Total Visits จากข้อความเป็นตัวเลข
    print("Converting Total Visits...")
    if "Total Visits" in df.columns:
        df["Total Visits"] = df["Total Visits"].apply(clean_total_visits)

    # 5. จัดการ Data Types 
    # (Active Users และ Favorites เป็น int อยู่แล้วตามที่ ingest มา แต่อาจจะมีการคำนวณที่ทำให้กลายเป็น float ตอนมีค่าว่าง จึงควรเช็คอีกรอบ)
    numeric_cols = ["Active Users", "Favorites", "Server Size"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('int64')

    print(f"Transformation complete. Remaining columns: {len(df.columns)}")
    return df

# ==========================================
# 5. LOAD TO PRODUCTION SCHEMA
# ==========================================
def load_to_production(engine, df):
    # สร้าง Schema production หากยังไม่มี
    with engine.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{PROD_SCHEMA}"'))
    print(f"Schema '{PROD_SCHEMA}' is ready.")

    print(f"Loading transformed data to {PROD_SCHEMA}.{TABLE_NAME}...")
    df.to_sql(
        name=TABLE_NAME,
        con=engine,
        schema=PROD_SCHEMA,
        if_exists="replace",
        index=False,
        chunksize=5000,
        method="multi"
    )
    print("Data load to production completed.")

# ==========================================
# 6. MAIN EXECUTION
# ==========================================
def main():
    print("======================================")
    print(" ROBLOX GAMES DATA - TRANSFORMATION")
    print("======================================")
    try:
        engine = create_db_engine()
        
        # Transform 
        transformed_df = transform_data(engine)
        
        # Load to Production
        load_to_production(engine, transformed_df)
        
        print("\nTRANSFORMATION COMPLETED SUCCESSFULLY!")
        engine.dispose()
        
    except Exception as error:
        print("\nTRANSFORMATION FAILED!")
        print(f"Error: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()