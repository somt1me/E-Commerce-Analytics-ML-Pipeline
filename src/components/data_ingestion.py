import os
import sys
import sqlite3
import pandas as pd
from dataclasses import dataclass
from src.exception import CustomException
from src.logger import logging

# 1. Define the output path configuration using @dataclass
@dataclass
class DataIngestionConfig:
    """
    DataIngestionConfig paths for raw and processed data
    """
    raw_data_dir: str = os.path.join("data", "raw_data")
    db_path: str = os.path.join("data", "raw_data", "data.db")

# 2. Main processing class
class DataIngestion:
    def __init__(self):
        # Initialize the path configuration object
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self) -> str:
        """
        Ingest raw data CSV files into SQLite database tables
        """
        # Đã sửa lỗi: logging.into -> logging.info
        logging.info("Entered the Data Ingestion component")
        try:
            raw_dir = self.ingestion_config.raw_data_dir
            if not os.path.exists(raw_dir):
                logging.warning(f"Raw data directory '{raw_dir}' does not exist. Please place data CSV files inside.")
                return self.ingestion_config.db_path

            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.ingestion_config.db_path), exist_ok=True)

            # Connect to SQLite database (Chỉ kết nối khi thư mục dữ liệu đã tồn tại)
            conn = sqlite3.connect(self.ingestion_config.db_path)
            logging.info(f"Connected to SQLite DB at: {self.ingestion_config.db_path}")

            # Iterate through raw CSV files and write to DB
            for file_name in os.listdir(raw_dir):
                if file_name.endswith(".csv"):
                    # Generate clean table name
                    table_name = file_name.replace(".csv", "")
                    file_path = os.path.join(raw_dir, file_name)

                    df = pd.read_csv(file_path)
                    # Insert data into SQLite table
                    df.to_sql(table_name, conn, if_exists="replace", index=False)
                    logging.info(f"Successfully loaded table [{table_name}] with {len(df)} rows")

            conn.close()
            logging.info("Data Ingestion completed successfully")
            return self.ingestion_config.db_path

        except Exception as e:
            raise CustomException(e, sys)

if __name__ == "__main__":
    obj = DataIngestion()
    obj.initiate_data_ingestion()