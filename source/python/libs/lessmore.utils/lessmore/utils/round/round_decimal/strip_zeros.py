def strip_zeros(s):
    return s.rstrip("0").rstrip(".") if "." in s else s


def test():
    assert strip_zeros("0.000") == "0"
    assert strip_zeros("0.001") == "0.001"


if __name__ == "__main__":
    test()
