def _auxiliary_function():
    """This is an auxiliary function. It is used in the modular function. It SHOULD be used in separate file if it contains some non-trivial logic"""

    # <some non-trivial logic>

    return "foo"


def test():
    """Every modular function SHOULD have at least one test function with basic usage and maybe some other tests."""
    assert _auxiliary_function() == "foo"


if __name__ == "__main__":
    test()
