import pickle

from typing import Any


def decode_from_pickle(value: bytes) -> Any:
    """Convert value from pickle.

    Parameters
    ----------
    value: bytes
        Value to convert

    Returns
    -------
    Any
        Unpickled value
    """
    return pickle.loads(value)


def test():
    print(decode_from_pickle(b"\x80\x03K\x01."))


if __name__ == "__main__":
    test()
