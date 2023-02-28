from insurance.logger import logging
from insurance.exception import InsuranceException
import os, sys


def test_logger_and_exception():
    try:
        logging.info("Starting of the test_logger_and_exception")
        result = 3 /10
        print(result)
        logging.info("Ending of the test_logger_and_exception")
    except Exception as e:
        logging.info(str(e))
        raise InsuranceException(e, sys)


if __name__ == "__main__":
    try:
        test_logger_and_exception()
    except Exception as e:
        print(e)