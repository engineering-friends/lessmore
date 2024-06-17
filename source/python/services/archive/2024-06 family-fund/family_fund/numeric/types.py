import numpy as np
import pandas as pd


def is_float(obj):
    return np.issubdtype(type(obj), float)


def is_int(obj):
    return np.issubdtype(type(obj), np.integer)


def is_numeric(obj):
    return is_int(obj) or is_float(obj)


def is_int_like(obj):
    if isinstance(obj, str) or is_float(obj):
        try:
            obj = float(obj)
            return int(obj) == obj
        except:
            return False
    elif is_int(obj):
        return True
    else:
        return False


def cast_int(obj, allow_none=False):
    if is_none(obj) and allow_none:
        return obj
    assert is_int_like(obj)

    return int(float(obj))


def is_float_like(obj):
    if is_float(obj):
        return True
    elif isinstance(obj, str):
        try:
            float(obj)
            return True
        except:
            return False
    return False


def test_is_int_like():
    print(is_int_like(1))
    print(is_int_like("1"))
    print(is_int_like("1.0"))
    print(is_int_like("1.2"))
    print(is_int_like("1.2;;"))
    print(cast_int("1.0"))
    print(cast_int(1.0))
    print(cast_int(1))
    print(cast_int(np.int64(1)))

    print(is_float_like("1.2;;"))
    print(is_float_like("1.2"))


def is_none(obj):
    if obj is None:
        return True
    else:
        try:
            if np.isnan(obj):
                return True
        except:
            pass

        try:
            if pd.isnull(obj):
                return True

        except:
            return False

    return False


if __name__ == "__main__":
    test_is_int_like()
