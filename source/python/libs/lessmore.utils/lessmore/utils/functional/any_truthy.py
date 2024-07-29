from typing import Iterable


def any_truthy(iterable: Iterable) -> bool:
    return any(item for item in iterable)


def test():
    assert not any_truthy([None, None, None])
    assert any_truthy([None, None, None, 1])
    assert not any_truthy([])


if __name__ == "__main__":
    test()
