import os
import sys
import shutil
import logging
from logging_config import setup_logging
from config import (
    PUBLIC_DIRECTORY,
    STATIC_DIRECTORY,
    CONTENT_DIRECTORY,
    TEMPLATE_FILE,
    DOCS_DIRECTORY,
)
from generator import static_to_public, generate_pages_recursive

setup_logging()
logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"

    if os.path.exists(DOCS_DIRECTORY):
        shutil.rmtree(DOCS_DIRECTORY)
        logger.info(f"Directory deleted: `{DOCS_DIRECTORY}`")

    try:
        static_to_public(STATIC_DIRECTORY, DOCS_DIRECTORY)
        generate_pages_recursive(
            CONTENT_DIRECTORY, TEMPLATE_FILE, DOCS_DIRECTORY, basepath
        )

    except Exception as e:
        logger.exception(f"Error: {e}")
        raise

    else:
        print("Done. All HTML content successfully created.")


if __name__ == "__main__":
    main()
