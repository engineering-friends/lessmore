import inspect
import os.path

from typing import Callable

from lessmore.utils.reflexion import load_module


def _get_self_functions_from_module(module_path: str) -> list[Callable]:
    """Get all functions in a module that have self as first argument"""

    # - Import module

    module = load_module(module_obj=module_path)

    # - Read code

    with open(module_path, "r") as f:
        module_code = f.read()

    # - Iterate over functions in module

    functions = []
    for x in dir(module):
        function = getattr(module, x)
        if callable(function) and f"def {function.__name__}(" in module_code:
            functions.append(function)

    # - Filter functions with self as first argument

    self_functions = []
    for function in functions:
        args = inspect.getfullargspec(function).args
        if args and args[0] == "self":
            self_functions.append(function)

    return self_functions


def test():
    assert [
        f.__name__
        for f in _get_self_functions_from_module(os.path.join(os.path.dirname(__file__), "_file_for_test.py"))
    ] == ["f"]


if __name__ == "__main__":
    test()
