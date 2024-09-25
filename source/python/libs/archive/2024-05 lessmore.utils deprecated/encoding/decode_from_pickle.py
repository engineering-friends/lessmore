import pickle

from typing import Any, Literal


def decode_from_pickle(value: bytes, library: Literal["pickle", "dill"] = "pickle") -> Any:
    """Convert value from pickle.

    Parameters
    ----------
    value: bytes
        Value to convert

    library: Literal['pickle', 'dill']
        Library to use

    Returns
    -------
    Any
        Unpickled value
    """

    if library == "pickle":
        return pickle.loads(value)
    elif library == "dill":
        import dill

        return dill.loads(value)


def test():
    print(decode_from_pickle(b"\x80\x03K\x01."))


if __name__ == "__main__":
    test()
