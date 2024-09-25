from typing import Any

import numpy as np


def is_any_float(value: Any):
    return np.issubdtype(type(value), np.float64)


def test():
    assert is_any_float(1.0)
    assert is_any_float(np.float64(1))
    assert not is_any_float(1)
    assert not is_any_float("1.0")


if __name__ == "__main__":
    test()
