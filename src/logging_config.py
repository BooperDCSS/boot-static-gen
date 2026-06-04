import logging
import sys

def setup_logging():

    logger = logging.getLogger()
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    console_logger = logging.StreamHandler(sys.stdout)
    console_logger.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_logger.setFormatter(console_formatter)

    file_logger = logging.FileHandler("report.log")
    file_logger.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter("[%(name)s] - %(asctime)s (%(levelname)s): %(message)s")
    file_logger.setFormatter(file_formatter)

    logger.addHandler(console_logger)
    logger.addHandler(file_logger)

    return logger

