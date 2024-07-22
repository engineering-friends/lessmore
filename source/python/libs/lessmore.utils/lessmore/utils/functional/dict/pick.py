def pick(d: dict, keys: list):
    return {k: d[k] for k in keys if k in d}


def test():
    assert pick({"a": 1, "b": 2, "c": 3}, ["a", "c"]) == {"a": 1, "c": 3}


if __name__ == "__main__":
    test()
