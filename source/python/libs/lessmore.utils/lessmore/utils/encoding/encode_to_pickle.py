import pickle

from typing import Any


def encode_to_pickle(value: Any, *args, **kwargs) -> bytes:
    """Convert value to pickle.

    Parameters
    ----------
    value: Any
        Value to convert

    Returns
    -------
    bytes
        Pickled value
    """
    return pickle.dumps(value, *args, **kwargs)


def test():
    print(encode_to_pickle(1))


if __name__ == "__main__":
    test()
