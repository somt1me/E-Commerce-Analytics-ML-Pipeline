import os
import sys
import pandas as pd
from sqlalchemy import create_engine 

# Import logger and custom exception from existing src files
from src.logger import logging
from src.exception import CustomException

# Define path constants
DB_PATH = os.path.join("database", "ecommerce.db")
RAW_DATA_PATH = os.path.join("data", "raw", "ecommerce_orders_dataset.csv")

def get_db_engine():
    """
    Create SQLalchemy engine for SQLite database
    """
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
        return engine
    except Exception as e:
        raise CustomException(e, sys)

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize DataFrame column names
    """
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
    )
    return df

def ingest_raw_data():
    """
    Ingest 2026 E-Commerce dataset into SQLite database table 'fact_orders'
    """
    logging.info("Starting data ingestion process...")

    try:
        if not os.path.exists(RAW_DATA_PATH):
            logging.error(f"File not found at '{RAW_DATA_PATH}'.")
            print(f"[ERROR] File not found at '{RAW_DATA_PATH}'. Please place 'ecommerce_orders_dataset.csv' in 'data/raw/'.")
            return

        engine = get_db_engine()

        # Read CSV file
        df = pd.read_csv(RAW_DATA_PATH)
        logging.info(f"Loaded CSV file with {len(df)} rows and {len(df.columns)} columns")

        # Clean column headers
        df = clean_column_names(df)

        # Ingest data frame into SQLite table 'fact_orders'
        df.to_sql("fact_orders", con=engine, if_exists="replace", index=False)

        logging.info(f"Successfully ingested data into table 'fact_orders' in '{DB_PATH}'")
        print(f"[SUCCESS] Ingested data into table 'fact_orders' in '{DB_PATH}'")

    except Exception as e:
        logging.error("Exception occurred during Data Ingestion")
        raise CustomException(e, sys)

if __name__ == "__main__":
    ingest_raw_data()