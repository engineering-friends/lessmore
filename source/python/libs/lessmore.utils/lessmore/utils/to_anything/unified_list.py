from typing import Iterable, Union

from loguru import logger
from sortedcontainers import SortedList


# todo later: sorted list and list are not the same. Take it out of class [@marklidenberg]

ListLike = Union[list, SortedList]


class UnifiedList:
    def __call__(self, value):
        logger.warning("unified_list() is deprecated and soon will be removed, use to_list() instead")
        return UnifiedList.to_list(value)

    @staticmethod
    def to_list(value):
        if isinstance(value, list):
            return value
        elif isinstance(value, SortedList):
            return list(value)
        elif isinstance(value, Iterable):
            return list(value)
        else:
            raise Exception("Unknown list type")

    @staticmethod
    def to_sorted_list(value, **kwargs):
        if isinstance(value, SortedList):
            return value
        else:
            value = UnifiedList.to_list(value)
            return SortedList(value, **kwargs)


unified_list = UnifiedList()


def to_list(value):
    return unified_list.to_list(value)


def to_sorted_list(value, **kwargs):
    return unified_list.to_sorted_list(value, **kwargs)


def test():
    assert to_list(["1", "2", "3"]) == ["1", "2", "3"]
    assert to_list("123") == ["1", "2", "3"]


if __name__ == "__main__":
    test()
