import json

from datetime import date, datetime
from typing import Callable


def printy_serializer(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    elif isinstance(value, (dict, list, set, tuple)):
        return json.dumps(value, default=str, ensure_ascii=False, sort_keys=True)
    elif isinstance(value, str):
        return value
    else:
        return str(value)


def printy(
    value,
    clip: bool = False,
    serializer: Callable = printy_serializer,
) -> str:
    # - Serialize

    value = serializer(value)

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
