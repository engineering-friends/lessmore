import sys

from typing import Any, Callable

from loguru import logger

from lessmore.utils.loguru_utils.format_as_json_colored.format_as_json_colored import format_as_json_colored
from lessmore.utils.loguru_utils.format_with_trace.format_with_trace import format_with_trace


IS_CONFIGURED = False


def configure_loguru(
    level: str = "DEBUG",
    sink: Any = sys.stdout,  # loguru sink
    formatter: Callable = format_as_json_colored,
    remove_others: bool = True,
    overwrite_config: bool = True,
):
    # - Preprocess arguments

    level = level.upper()

    # - Check if loguru is already configured

    global IS_CONFIGURED

    if IS_CONFIGURED:
        if not overwrite_config:
            raise Exception("Already configured loguru")
        else:
            logger.warning("Reconfiguring loguru")

    # - Reset loguru logger

    if remove_others:
        logger.remove()

    # - Add sink

    logger.add(sink, level=level, format=formatter)

    # - Set IS_CONFIGURED to True

    IS_CONFIGURED = True
