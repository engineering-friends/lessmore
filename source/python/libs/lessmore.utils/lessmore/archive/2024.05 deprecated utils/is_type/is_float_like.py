from typing import Any

from lessmore.utils.is_type.is_any_float import is_any_float


def is_float_like(value: Any):
    if is_any_float(value):
        return True
    elif isinstance(value, str):
        try:
            float(value)
            return True
        except:
            return False
    else:
        return False


def test():
    import numpy as np

    assert is_float_like(1.0)
    assert is_float_like(np.float64(1))
    assert is_float_like("1.0")
    assert is_float_like("1.2")
    assert not is_float_like(1)
    assert not is_float_like("1.2;;")


if __name__ == "__main__":
    test()
