from lessmore.utils.is_type.is_any_float import is_any_float
from lessmore.utils.is_type.is_any_int import is_any_int


def is_int_like(obj):
    if isinstance(obj, str) or is_any_float(obj):
        try:
            obj = float(obj)
            return int(obj) == obj
        except:
            return False
    elif is_any_int(obj):
        return True
    else:
        return False


def test():
    assert is_int_like(1)
    assert is_int_like(1.0)
    assert is_int_like("1")
    assert is_int_like("1.0")
    assert is_int_like("1.000")
    assert not is_int_like("1.001")


if __name__ == "__main__":
    test()
