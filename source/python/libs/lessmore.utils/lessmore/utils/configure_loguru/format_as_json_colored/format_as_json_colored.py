import json
import math
import sys

from collections import OrderedDict
from typing import Any

from loguru import logger

from lessmore.utils.configure_loguru.format_as_json_colored._add_color_tags_to_json import _add_color_tags_to_json
from lessmore.utils.configure_loguru.get_stack import get_stack
from lessmore.utils.to_anything.to_datetime import to_datetime


try:
    from loguru import Record
except ImportError:
    # for some reason, Record does not import this way in loguru 0.6.0
    Record = Any


def format_as_json_colored(record: Record):
    # - Validate record

    assert "_json" not in record["extra"]

    # - Pop extra

    extra = dict(record["extra"])
    extra.pop("source", None)

    # - Create record_dic that will be serialized as json

    record_dic = {
        "message": record["message"],
        "module": record["module"],
        "ts": to_datetime(record["time"]).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],  # 2023-03-26 13:04:09.512
        "source": record["extra"].get("source", ""),
    }

    if record["exception"]:
        record_dic["stack"] = get_stack(exception=record["exception"])
        record_dic["error"] = record_dic["stack"].split("\n")[-1]

    record_dic = {k: v for k, v in record_dic.items() if v}
    record_dic.update(extra)

    # - Sort keys

    record_dic = OrderedDict(
        sorted(
            record_dic.items(),
            key=lambda kv: {
                "ts": 0,
                "module": 1,
                "message": 2,
                "source": 3,
                "extra": 4,
                "error": 5,
                "stack": 6,
                "level": 7,
            }.get(
                kv[0], 4
            ),  # default is extra
        )
    )

    # - Dump json and add it to record

    return _add_color_tags_to_json(record_dic=record_dic, record=record)


def test():
    logger.info("Simple message")
    logger.info("Message with extra", foo="bar")

    try:
        raise ValueError("This is an exception")
    except ValueError:
        logger.exception("Exception caught")


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, format=format_as_json_colored)
    test()
