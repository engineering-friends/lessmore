import inspect

from typing import Callable


def kwargs_to_args(func: Callable, kwargs: dict) -> list:
    # - Get function signature

    signature = inspect.signature(func)

    # - Get function parameters in right order

    parameters_by_its_name = signature.parameters  # OrderedDict([('a', <Parameter "a">), ('b', <Parameter "b=2">)])

    # - Get args

    args = [kwargs.get(k, v.default) for k, v in parameters_by_its_name.items()]

    # - Check if all args are present

    assert all(arg is not inspect.Parameter.empty for arg in args), "Missing keyword arguments for function"

    # - Return args

    return args


def test():
    def f(a, b=2):
        print(a, b)

    assert (
        kwargs_to_args(
            func=f,
            kwargs={"a": 1},
        )
    ) == [1, 2]


if __name__ == "__main__":
    test()
