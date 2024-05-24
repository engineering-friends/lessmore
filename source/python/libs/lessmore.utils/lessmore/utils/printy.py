from datetime import date, datetime
from typing import Any


try:
    import ujson as json
except ImportError:
    import json


def printy(
    value: Any,
    clip: bool = False,
    jsonify: bool = True,
    json_dumps_kwargs={"default": str, "indent": 1, "ensure_ascii": False, "sort_keys": True},
):
    # - Dumps

    if not isinstance(value, str):
        if jsonify and isinstance(value, (dict, list, set, tuple, datetime, date)):
            value = json.dumps(
                value,
                **json_dumps_kwargs,
            )
        else:
            value = str(value)

    # - Clip

    if clip:
        import pyperclip

        pyperclip.copy(value)

    # - Print

    print(value)

    # - Return

    return value


def test():
    printy({"a": 1, "b": 2})
    v = printy({"a": 1, "b": 2}, clip=True)
    assert (
        v
        == """\
{
 "a": 1,
 "b": 2
}"""
    )


if __name__ == "__main__":
    test()
