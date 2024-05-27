import sys

from loguru import logger

from lessmore.utils.loguru_utils.format_with_trace._exception_formatter import _exception_formatter
from lessmore.utils.loguru_utils.format_with_trace._extra_formatter import _extra_formatter


def format_with_trace(
    record,
    formatters=(
        lambda record: "<green>{time:YYYY-MM-DD HH:mm:ss!UTC}</green>",
        lambda record: "<cyan>{module}</cyan>",
        lambda record: "<level>{message}</level>",
        _extra_formatter,
        _exception_formatter,
    ),
    separator=" | ",
):
    # workaround for custom extra
    record["extra"]["_extra"] = {k: v for k, v in dict(record["extra"]).items() if not k.startswith("_")}
    values = [formatter(record) for formatter in formatters]
    values = [value for value in values if value]
    return separator.join(values) + "\n"


def test():
    logger.info("Simple message")
    logger.info("Message with extra", extra={"foo": "bar"})

    try:
        raise ValueError("This is an exception")
    except ValueError:
        logger.exception("Exception caught")


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, format=format_with_trace)
    test()
