from typing import Any, Union


def contains_nested(a: list | dict | str | int | Any, b: Union[list, dict, str | int | Any]) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        for key in b:
            if key not in a:
                return False
            if not contains_nested(a[key], b[key]):
                return False
        return True
    elif isinstance(a, list) and isinstance(b, list):
        for i in range(len(b)):
            if not contains_nested(a[i], b[i]):
                return False
        return True
    else:
        return a == b


def test():
    assert contains_nested({"a": 1, "b": ["foo", {"c": ["z"]}]}, {"a": 1, "b": ["foo", "bar", {"c": ["x", "y", "z"]}]})


if __name__ == "__main__":
    test()
