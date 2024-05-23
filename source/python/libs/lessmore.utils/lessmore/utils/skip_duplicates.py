from typing import Callable, Iterable


def skip_duplicates(values: Iterable, key: Callable = lambda x: x) -> list:
    # preserves order of sequence
    seen = set()
    return [x for x in values if not (key(x) in seen or seen.add(key(x)))]


def test():
    assert skip_duplicates([2, 2, 1, 1, 3, 3]) == [2, 1, 3]


if __name__ == "__main__":
    test()
