from itertools import filterfalse
from typing import Iterable


def filter_non_empty(iterable: Iterable) -> Iterable:
    return filter(None, iterable)


def filter_empty(iterable: Iterable) -> Iterable:
    return filterfalse(None, iterable)


def test():
    assert list(filter_non_empty([1, 2, 3, "", 4, 5, None])) == [1, 2, 3, 4, 5]
    assert list(filter_empty([1, 2, 3, None, 4, 5, None])) == [None, None]


if __name__ == "__main__":
    test()
