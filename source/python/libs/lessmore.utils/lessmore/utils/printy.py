import json

from datetime import date, datetime
from typing import Any, Callable, Optional, Union


def json_serializer(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    elif isinstance(value, (dict, list, set, tuple)):
        return json.dumps(value, default=str, ensure_ascii=False, sort_keys=True)
    else:
        return value


DEFAULT_SERIALIZER = "DEFAULT_SERIALIZER"


class Printy:
    def __init__(
        self,
        serializer: Optional[Callable] = json_serializer,
    ):
        self.serializer = serializer

    def __call__(
        self,
        value: Any,
        clip: bool = False,
        serializer: Union[None, Callable, DEFAULT_SERIALIZER] = DEFAULT_SERIALIZER,
    ):
        # - Get serializer

        if serializer == DEFAULT_SERIALIZER:
            serializer = self.serializer
        elif serializer is None:
            serializer = lambda x: x

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


# global instance
printy = Printy()


def test():
    printy({"a": 1, "b": 2})
    v = printy({"a": 1, "b": 2}, clip=True)
    assert v == '{"a": 1, "b": 2}'


if __name__ == "__main__":
    test()
