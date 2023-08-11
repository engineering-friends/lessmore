import json
import math
import sys

from loguru import logger

from lessmore.utils.loguru_utils.format_with_trace._get_stack import _get_stack


def format_as_json(record):
    assert "_json" not in record["extra"]

    extra = dict(record["extra"])
    extra.pop("source", None)

    record_dic = {
        "level": record["level"].name,
        "message": record["message"],
        "ts": int(math.floor(record["time"].timestamp() * 1000)),  # epoch millis
        "source": record["extra"].get("source", ""),
        "extra": extra,
        "stack": "",
        "error": "",
    }

    if record["exception"]:
        record_dic["stack"] = _get_stack(record["exception"])
        record_dic["error"] = record_dic["stack"].split("\n")[-1]

    record["extra"]["_json"] = json.dumps(record_dic, default=str)
    return "{extra[_json]}\n"


def test():
    logger.info("Simple message")
    logger.info("Message with extra", extra={"foo": "bar"})

    try:
        raise ValueError("This is an exception")
    except ValueError:
        logger.exception("Exception caught")


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, format=format_as_json)
    test()
