from lessmore.utils.is_type.is_any_int import is_any_int
from lessmore.utils.numeric.types import is_float


def is_int_like(obj):
    if isinstance(obj, str) or is_float(obj):
        try:
            obj = float(obj)
            return int(obj) == obj
        except:
            return False
    elif is_any_int(obj):
        return True
    else:
        return False
