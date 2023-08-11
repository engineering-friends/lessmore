from typing import Union

from loguru import logger


BoolLike = Union[bool, str, int, float]


class UnifiedBool:
    def __call__(self, value):
        logger.warning("unified_bool() is deprecated and soon will be removed, use to_bool() instead")
        return UnifiedBool.to_bool(value)

    @staticmethod
    def to_bool(value):
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

    @staticmethod
    def to_str(value):
        value = UnifiedBool.to_bool(value)
        return str(value)

    @staticmethod
    def to_string(value):
        logger.warning("UnifiedBool.to_string is deprecated, use UnifiedBool.to_str instead")
        return UnifiedBool.to_str(value)

    @staticmethod
    def to_int(value):
        value = UnifiedBool.to_bool(value)
        return int(value)

    @staticmethod
    def to_integer(value):
        logger.warning("UnifiedBool.to_integer is deprecated, use UnifiedBool.to_int instead")
        return UnifiedBool.to_int(value)

    @staticmethod
    def to_float(value):
        value = UnifiedBool.to_bool(value)
        return float(value)


unified_bool = UnifiedBool()


def to_bool(value):
    """Converts any input to bool."""
    return unified_bool.to_bool(value)


def to_bool_int(value):
    """1 or 0"""
    return unified_bool.to_int(value)


def to_bool_float(value):
    """1.0 or 0.0"""
    return unified_bool.to_float(value)


def to_bool_str(value):
    """ "True" or "False" """
    return unified_bool.to_str(value)


def test():
    for value in [1, "y", "yes", "True", "1"]:
        assert to_bool(value) is True

    for value in [0, "n", "no", "False", "0"]:
        assert to_bool(value) is False

    print(to_bool_float("True"))


if __name__ == "__main__":
    test()
