from datetime import date, datetime
from typing import Any


try:
    import ujson as json
except ImportError:
    import json


def better_print(
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
    better_print({"a": 1, "b": 2})
    better_print(better_print)


if __name__ == "__main__":
    test()
