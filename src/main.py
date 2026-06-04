import os
import shutil
import logging
from logging_config import setup_logging
from config import PUBLIC_DIRECTORY, STATIC_DIRECTORY, ROOT_DIRECTORY, CONTENT_DIRECTORY, TEMPLATE_FILE
from generator import static_to_public, generate_page, generate_pages_recursive

setup_logging()
logger = logging.getLogger(__name__)



def main():
    if os.path.exists(PUBLIC_DIRECTORY):
        shutil.rmtree(PUBLIC_DIRECTORY)
        logger.info(f"Directory deleted: `{PUBLIC_DIRECTORY}`")

    try:
        static_to_public(STATIC_DIRECTORY, PUBLIC_DIRECTORY)
#        generate_page("content/index.md", TEMPLATE_FILE, "public/index.html")
#        generate_pages_recursive(CONTENT_DIRECTORY, TEMPLATE_FILE, PUBLIC_DIRECTORY)
        
    except Exception as e:
        logger.exception(f"Error: {e}")
        raise

    else:
        print(f"Done. All HTML content successfully created.")


if __name__ == "__main__":
    main()
