from typing import Union


BoolLike = Union[bool, str, int, float]


def to_bool(value: BoolLike) -> bool:
    """Converts bool-like values to bool."""
    if isinstance(value, bool):
        return value
    elif isinstance(value, (int, float)):
        if value == 1:
            return True
        elif value == 0:
            return False
        else:
            raise Exception(f"Unknown bool int format: {value}")
    elif isinstance(value, str):
        if value.lower() in ["y", "yes", "true", "1"]:
            return True
        elif value.lower() in ["n", "no", "false", "0"]:
            return False
        else:
            raise Exception(f"Unknown bool string format: {value}")
    else:
        raise Exception(f"Unknown bool format: {type(value)}")


def test():
    for value in [1, "y", "yes", "True", "1"]:
        assert to_bool(value) is True

    for value in [0, "n", "no", "False", "0"]:
        assert to_bool(value) is False


if __name__ == "__main__":
    test()
