import sys

from collections import OrderedDict
from typing import Any

from loguru import logger

from lessmore.utils.loguru_utils.formatters.format_as_colored_json._add_color_tags_to_json import (
    _add_color_tags_to_json,
)
from lessmore.utils.loguru_utils.formatters.get_traceback import get_traceback
from lessmore.utils.to_anything.to_datetime import to_datetime


try:
    from loguru import Record
except ImportError:
    # for some reason, Record does not import this way in loguru 0.6.0
    Record = Any


def format_as_colored_json(append_non_json_traceback: bool = True):
    """Loguru formatter builder for colored json logs.

    Sample output (colored in the console):
    {"ts": "2024-07-29 08:19:03.675", "module": "format_as_colored_json", "message": "Simple message"}
    {"ts": "2024-07-29 08:19:03.675", "module": "format_as_colored_json", "message": "Message with extra", "foo": "bar"}
    {"ts": "2024-07-29 08:19:03.675", "module": "format_as_colored_json", "message": "Exception caught", "error": "ValueError: This is an exception", "traceback": "...\nValueError: This is an exception"}

    Parameters
    ----------
    append_non_json_traceback : bool
        If True, extra traceback will be appended to the log, as if we use the vanilla formatter.

    """

    def _format_as_json_colored(record: Record):
        # - Validate record

        assert "_json" not in record["extra"]

        # - Pop extra

        extra = dict(record["extra"])
        extra.pop("source", None)

        # - Create record_dic that will be serialized as json

        record_dic = {
            "msg": record["message"],
            # "module": record["module"],
            "ts": to_datetime(record["time"]).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],  # 2023-03-26 13:04:09.512
            "source": record["extra"].get("source", ""),
        }

        if record["exception"]:
            record_dic["traceback"] = get_traceback(exception=record["exception"]).strip()
            record_dic["error"] = record_dic["traceback"].split("\n")[-1]

        record_dic = {k: v for k, v in record_dic.items() if v}
        record_dic.update(extra)

        # - Sort keys

        record_dic = OrderedDict(
            sorted(
                record_dic.items(),
                key=lambda kv: {
                    "ts": 0,
                    # "module": 1,
                    "msg": 2,
                    "source": 3,
                    "extra": 4,
                    "error": 5,
                    "traceback": 6,
                    "level": 7,
                }.get(kv[0], 4),  # default is extra
            )
        )

        # - Dump json and add it to record

        return _add_color_tags_to_json(
            record_dic=record_dic,
            record=record,
            append_non_json_traceback=append_non_json_traceback,
        )

    return _format_as_json_colored


def test():
    logger.info("Simple message")
    logger.info("Message with extra", foo="bar")

    try:
        raise ValueError("This is an exception")
    except ValueError:
        logger.exception("Exception caught")


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stdout, format=format_as_colored_json(append_non_json_traceback=True))
    test()
