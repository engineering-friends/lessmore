from lessmore.utils.modular_code.modular_function._auxiliary_function import _auxiliary_function


def modular_function():
    """
    This is a modular function. All other functions SHOULD usually be used in separate files if they contain some non-trivial logic

    If a modular function has auxiliary functions, we create a separate folder for that function with the same name.
    Overall in this case we will have file `modular_function/modular_function.py` containing function `modular_function`

    """

    return _auxiliary_function() + " bar"


def test():
    """Every modular function SHOULD have at least one test function with basic usage and maybe some other tests."""

    assert modular_function() == "foo bar"


if __name__ == "__main__":
    test()
