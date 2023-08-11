from typing import Any

import numpy as np


def is_any_int(value: Any):
    return np.issubdtype(type(value), np.integer)


def test():
    assert is_any_int(1)
    assert is_any_int(np.int64(1))
    assert not is_any_int(1.0)
    assert not is_any_int("1.0")


if __name__ == "__main__":
    test()
