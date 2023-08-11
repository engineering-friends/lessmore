import collections.abc
import json
import sys

from copy import deepcopy

from loguru import logger

from lessmore.utils.loguru_utils.format_with_trace._get_stack import _get_stack


def merge_dict_inline(
    d: dict,  # SIDE EFFECTED
    u: dict,
) -> dict:
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = merge_dict_inline(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def format_as_json_loggia(record, extras=None):
    """https://github.com/deeplay-io/loggia/blob/master/docs/log-structure.md

      Sample:   {
      "@timestamp": "2021-03-30T08:23:27.013Z",
      "message": "Something happened",
      "data": {"times": 42},
      "logLevel": 30,
      "labels": {"accountId": "1111", "tableId": "2222"},
      "ttlHours": 168
    }
    """
    extra = dict(record["extra"])
    merge_dict_inline(extra, extras or {})
    labels = extra.pop("labels", None)
    ttl_hours = extra.pop("ttl_hours", None)

    record_dic = {
        "@timestamp": record["time"].isoformat(),
        "logLevel": 10 if record["level"].no == 5 else record["level"].no + 10,  # trace: 5 -> 10, other: x -> x + 10
        "message": record["message"],
    }

    if record["exception"]:
        trace = _get_stack(record["exception"])
        trace_lines = [line for line in trace.split("\n") if line]
        extra["exception"] = {"traceback": trace, "message": trace_lines[-1]}

    if labels:
        record_dic["labels"] = labels
    if ttl_hours:
        record_dic["ttlHours"] = ttl_hours
    if extra:
        extra["@@type"] = "JSON"
        record_dic["data"] = extra

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
    logger.add(sys.stderr, format=format_as_json_loggia)
    test()
