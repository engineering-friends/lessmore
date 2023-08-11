from lessmore.utils.is_type.is_any_float import is_any_float
from lessmore.utils.is_type.is_any_int import is_any_int


def is_numeric(obj):
    return is_any_int(obj) or is_any_float(obj)


def test():
    import numpy as np
    assert is_numeric(1.0)
    assert is_numeric(np.float64(1))
    assert is_numeric(1)
    assert is_numeric(np.int64(1))
    assert not is_numeric("1.0")
    assert not is_numeric("1")
    assert not is_numeric("1.2")
    assert not is_numeric("1.2;;")

if __name__ == '__main__':
    test()