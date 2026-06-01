import os
import shutil
import logging
from config import PUBLIC_DIRECTORY, STATIC_DIRECTORY

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="report.log",
    level=logging.DEBUG,
    format="%(asctime)s (%(levelname)s): %(message)s",
)


def static_to_public(source, target):
    source_dir_list = os.listdir(source)
    if os.path.exists(target):
        shutil.rmtree(target)
        logger.debug(f"Directory deleted: {target}")
    os.mkdir(target)
    logger.debug(f"Directory created: {target}")
    print(source_dir_list)
    for item in source_dir_list:
        if os.path.isfile(os.path.normpath(os.path.join(source, item))):
            shutil.copy(os.path.join(source, item), target)
            logger.debug(f"File `{item}` copied to `{target}`")
        elif os.path.isdir(os.path.normpath(os.path.join(source, item))):
            static_to_public(
                os.path.normpath(os.path.join(source, item)),
                os.path.normpath(os.path.join(target, item)),
            )
            logger.debug(f"Directory `{item}` copied to `{target}`")


def main():
    static_to_public(STATIC_DIRECTORY, PUBLIC_DIRECTORY)


if __name__ == "__main__":
    main()
