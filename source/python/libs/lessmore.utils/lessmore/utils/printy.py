import json

from datetime import date, datetime
from typing import Any, Callable, Optional


def printy(
    value: Any,
    clip: bool = False,
    serializer: Optional[Callable] = lambda value: json.dumps(value, default=str, ensure_ascii=False, sort_keys=True),
):
    # - Dumps

    if not isinstance(value, str):
        if serializer and isinstance(value, (dict, list, set, tuple, datetime, date)):
            value = serializer(value)
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
    assert v == '{"a": 1, "b": 2}'


if __name__ == "__main__":
    test()
