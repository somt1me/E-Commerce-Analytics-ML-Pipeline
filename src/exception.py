import sys
from src.logger import logging

def error_message_detail(error: Exception, error_detail: sys) -> str:
    """
    Extrace file name, line number, and error message     
    """

    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename

    error_message = (
        f"Error occured in Python script name [{file_name}]"
        f"Line number [{exc_tb.tb_lineno}]"
        f"Error message [{str(error)}]"
    )
    return error_message

class CustomException(Exception):
    def __init__(self, error_message: Exception, error_detail: sys) -> None:
        super().__init__(error_message)
        # Format detailed error message 
        self.error_message = error_message_detail(error_message, error_detail)

    def __str__(self) -> str:
        return self.error_message

if __name__ == "__main__":
    try:
        a = 1 / 0
    except Exception as e:
        logging.info("Testing Custom Exception")
        raise CustomException(e, sys)