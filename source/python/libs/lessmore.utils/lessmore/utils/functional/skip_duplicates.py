from typing import Callable, Iterable, Iterator


def skip_duplicates(values: Iterable, key: Callable = lambda x: x) -> Iterator:
    seen = set()
    for x in values:
        k = key(x)
        if k not in seen:
            seen.add(k)
            yield x


def test():
    assert list(skip_duplicates([2, 2, 1, 1, 3, 3])) == [2, 1, 3]


if __name__ == "__main__":
    test()
