import os
import sys
import shutil
import logging
from config import PUBLIC_DIRECTORY, STATIC_DIRECTORY

""" Logger Config """
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_logger = logging.StreamHandler(sys.stdout)
console_logger.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(levelname)s: %(message)s")
console_logger.setFormatter(console_formatter)

file_logger = logging.FileHandler("report.log")
file_logger.setLevel(logging.DEBUG)
file_formatter = logging.Formatter("%(asctime)s (%(levelname)s): %(message)s")
file_logger.setFormatter(file_formatter)

logger.addHandler(console_logger)
logger.addHandler(file_logger)

""" Copy function and main begin here """
def static_to_public(source, target):
    try:
        source_dir_list = os.listdir(source)
        if os.path.exists(target):
            shutil.rmtree(target)
            logger.debug(f"Directory deleted: `{target}`")
        os.mkdir(target)
        logger.info(f"Directory created: `{os.path.relpath(target)}`")
    except Exception as e:
        logger.error(
            f"mkdir/rmtree operation failed: {e}. Check source and target variables in src/config.py"
        )
        raise Exception(f"mkdir/rmtree operation failed: {e}. Check source and target variables in src/config.py")

    try:
        for item in source_dir_list:
            file_path = os.path.normpath(os.path.join(source, item))
            target_path = os.path.normpath(os.path.join(target, item))
            if os.path.isfile(file_path):
                shutil.copy(file_path, target)
                logger.info(f"File `{os.path.relpath(file_path)}` copied to `{os.path.relpath(target)}`")
            elif os.path.isdir(file_path):
                static_to_public(
                    file_path,
                    target_path,
                )
    except Exception as e:
        logger.error(
            f"copy operation failed: {e}. Check source and target variables in src/config.py"
        )
        raise Exception(f"copy operation failed: {e}. Check source and target variables in src/config.py")

def main():
    static_to_public(STATIC_DIRECTORY, PUBLIC_DIRECTORY)


if __name__ == "__main__":
    main()
