import os

from lessmore.utils.wise_comments.file_types import get_file_type, type_config
from lessmore.utils.wise_comments.wise_comments_formatter import WiseCommentsFormatter
from loguru import logger


def format_file(filename):
    logger.debug("Formatting file", filename=filename)

    # - Check if not exists

    if not os.path.exists(filename):
        raise Exception(f"File not found: {filename}")

    # - Read

    with open(filename, encoding="utf-8") as f:
        text = f.read()

    # - Get file type

    file_type = get_file_type(filename)

    # - Format

    for type_group, values in type_config.items():
        if file_type not in values["file_types"]:
            continue
        text = WiseCommentsFormatter(**values["wise_comments_config"]).format(text)

    # - Write

    # -- Write to tmp copy

    with open(filename + ".tmp", "w", encoding="utf-8") as f:
        f.write(text)

    # -- Replace original file

    os.replace(filename + ".tmp", filename)
