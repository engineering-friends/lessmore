from typing import Any, Literal


def encode_to_pickle(value: Any, library: Literal["pickle", "dill"] = "pickle", **kwargs) -> bytes:
    """Convert value to pickle.

    Parameters
    ----------
    value: Any
        Value to convert

    library: Literal['pickle', 'dill']
        Library to use

    Returns
    -------
    bytes
        Pickled value
    """

    if library == "pickle":
        import pickle

        return pickle.dumps(value, **kwargs)
    elif library == "dill":
        import dill

        return dill.dumps(value, **kwargs)


def test():
    print(encode_to_pickle(1, library="pickle"))
    print(encode_to_pickle(1, library="dill"))


if __name__ == "__main__":
    test()
