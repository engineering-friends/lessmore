from collections import defaultdict
from dataclasses import asdict, is_dataclass
from typing import Union

from box import Box
from loguru import logger


DictLike = Union[dict, Box]


class UnifiedDict:
    def __call__(self, value):
        logger.warning("unified_dict() is deprecated and soon will be removed, use to_dict() instead")
        return UnifiedDict.to_dict(value)

    @staticmethod
    def to_dict(value):
        if isinstance(value, dict):
            return value
        elif isinstance(value, (defaultdict, Box)):
            return dict(value)

        else:
            raise Exception("Unknown dictionary type")

    @staticmethod
    def to_default_dict(value, default_factory=None):
        if isinstance(value, defaultdict):
            return value
        else:
            value = UnifiedDict.to_dict(value)
            result = defaultdict(default_factory, value)
            return result

    @staticmethod
    def to_box(value, **kwargs):
        if isinstance(value, Box):
            return value
        else:
            value = UnifiedDict.to_dict(value)
            return Box(value, **kwargs)


unified_dict = UnifiedDict()


def to_dict(value):
    return unified_dict.to_dict(value)


def to_default_dict(value, default_factory=None):
    return unified_dict.to_default_dict(value, default_factory)


def to_box(value, **kwargs):
    return unified_dict.to_box(value, **kwargs)


def test():
    assert to_dict({"a": 1, "b": 2}) == {"a": 1, "b": 2}

    box = to_box({"a": 1, "b": 2})
    assert box.a == 1

    assert to_dict(box) == {"a": 1, "b": 2}


if __name__ == "__main__":
    test()
