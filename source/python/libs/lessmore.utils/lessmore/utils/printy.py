import json

from datetime import date, datetime
from typing import Any, Callable


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
    value: Any,
    clip: bool = True,
    serializer: Callable = printy_serializer,
) -> str:
    """Print and optionally copy to clipboard a value. Useful for debugging.

    Usually used as `from lessmore.utils.printy import printy as print`.

    """

    # - Serialize

    value = serializer(value)

    # - Clip

    if clip:
        try:
            import pyperclip

            pyperclip.copy(value)
        except:
            pass

    # - Print

    print(value)

    # - Return

    return value


def test():
    printy({"a": 1, "b": 2})

    assert printy({"a": 1, "b": 2}) == '{"a": 1, "b": 2}'


# test 1

if __name__ == "__main__":
    test()

# test 2
