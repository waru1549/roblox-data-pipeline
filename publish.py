import os
import sys
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

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

PROD_SCHEMA = "production"
TABLE_NAME = "roblox_games_data"

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Roblox_Dashboard_Data")

# ==========================================
# 2. DATABASE & GOOGLE SHEETS CONNECTION
# ==========================================
def get_db_engine():
    connection_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(connection_url, pool_pre_ping=True)

def connect_google_sheets():
    if not CREDENTIALS_FILE.exists():
        raise FileNotFoundError(f"Missing Service Account key: {CREDENTIALS_FILE}")
    
    print("Authenticating with Google Sheets API...")
    gc = gspread.service_account(filename=str(CREDENTIALS_FILE))
    return gc

# ==========================================
# 3. LOAD AND AGGREGATE DATA
# ==========================================
def load_and_prepare_data(engine):
    print(f"Reading data from {PROD_SCHEMA}.{TABLE_NAME}...")
    df = pd.read_sql_table(TABLE_NAME, con=engine, schema=PROD_SCHEMA)
    
    print("Aggregating data to daily snapshot to optimize for Google Sheets...")
    # ลดความถี่ข้อมูลจากระดับนาที/ชั่วโมง เป็นระดับวัน เพื่อเลี่ยงข้อจำกัด Cell Limit
    df['Date'] = pd.to_datetime(df['Date']).dt.date
    
    # สรุปข้อมูลรายวันของแต่ละเกม
    agg_funcs = {
        'Active Users': 'mean',
        'Favorites': 'max',
        'Total Visits': 'max',
        'Server Size': 'max',
        'Genre': 'first',
        'Title': 'first',
        'Creator': 'first',
        'Category': 'first'
    }
    
    daily_df = df.groupby(['Date', 'gameID'], as_index=False).agg(agg_funcs)
    
    # ปัดเศษ Active Users และแปลงกลับเป็น int
    daily_df['Active Users'] = daily_df['Active Users'].round(0).astype(int)
    
    print(f"Data compressed from {len(df):,} to {len(daily_df):,} rows.")
    return daily_df

# ==========================================
# 4. PUBLISH TO GOOGLE SHEETS
# ==========================================
def publish_to_sheets(gc, df):
    print(f"Opening Google Sheet: '{SHEET_NAME}'...")
    try:
        sh = gc.open(SHEET_NAME)
        worksheet = sh.sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        raise Exception(f"Spreadsheet '{SHEET_NAME}' not found. Make sure it is shared with the Service Account email.")

    print("Clearing old data in the worksheet...")
    worksheet.clear()

    print("Uploading DataFrame to Google Sheets...")
    set_with_dataframe(worksheet, df)
    print("Upload completed!")

# ==========================================
# 5. MAIN EXECUTION
# ==========================================
def main():
    print("======================================")
    print(" ROBLOX GAMES DATA - PUBLICATION")
    print("======================================")
    try:
        engine = get_db_engine()
        df = load_and_prepare_data(engine)
        
        gc = connect_google_sheets()
        publish_to_sheets(gc, df)
        
        print("\nPUBLICATION COMPLETED SUCCESSFULLY!")
        engine.dispose()
        
    except Exception as error:
        print("\nPUBLICATION FAILED!")
        print(f"Error: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()