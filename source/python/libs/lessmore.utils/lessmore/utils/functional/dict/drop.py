def drop(d: dict, keys: list):
    return {k: v for k, v in d.items() if k not in keys}


def test():
    assert drop({"a": 1, "b": 2, "c": 3}, ["a", "b"]) == {"c": 3}


if __name__ == "__main__":
    test()
