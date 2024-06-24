import sys

from lessmore.utils.loguru_utils.format_as_colored_json.format_as_colored_json import format_as_colored_json
from loguru import logger


def setup_json_loguru(
    level: str = "DEBUG",
    append_non_json_traceback: bool = True,
    remove_existing_sinks: bool = True,
):
    if remove_existing_sinks:
        logger.remove()

    logger.add(
        sink=sys.stdout,
        level=level,
        format=format_as_colored_json(append_non_json_traceback=append_non_json_traceback),
    )
