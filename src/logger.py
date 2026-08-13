import os
import logging
from datetime import datetime

# Generate log file name based on current timestamp 
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"

# Set up directory path for logs 
logs_path = os.path.join(os.getcwd(), "logs")
os.makedirs(logs_path, exist_ok=True)

LOG_FILE_PATH = os.path.join(logs_path, LOG_FILE)

# Configure logging format
logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO  # Keep only a single 'level' parameter here
)

if __name__ == "__main__":
    logging.info("Logging module initialized successfully / Module Logging đã khởi tạo thành công")