import numpy as np
import pandas as pd


def is_none_like(obj):
    # - Try None

    if obj is None:
        return True

    # - Try np.isnan

    try:
        if np.isnan(obj):
            return True
    except:
        pass

    # - Try pd.isnull

    try:
        if pd.isnull(obj):
            return True
    except:
        pass

    #  - False otherwise

    return False


def test():
    assert is_none_like(None)
    assert is_none_like(np.nan)
    assert is_none_like(pd.NA)
    assert not is_none_like("")
    assert not is_none_like(0)


if __name__ == "__main__":
    test()
