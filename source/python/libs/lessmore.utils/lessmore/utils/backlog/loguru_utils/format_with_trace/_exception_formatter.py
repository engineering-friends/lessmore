from lessmore.utils.loguru_utils.format_with_trace._get_stack import _get_stack


def _exception_formatter(record):
    if not record["exception"]:
        return

    assert all(key not in record["extra"] for key in ["_stack", "_error"])

    record["extra"]["_stack"] = _get_stack(record["exception"])
    record["extra"]["_error"] = record["extra"]["_stack"].split("\n")[-1]
    _extra = dict(record["extra"])
    _extra.pop("_stack")
    _extra.pop("_error")
    record["extra"]["_extra"] = _extra
    return "<red>{extra[_error]}</red>\n<red>{extra[_stack]}</red>"


# see test at format_with_trace.py
