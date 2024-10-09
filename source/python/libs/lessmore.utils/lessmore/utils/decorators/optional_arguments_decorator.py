import asyncio

from typing import Callable


def optional_arguments_decorator(func: Callable):
    """Enables the use of arguments in the decorator, without the need to wrap the function in a lambda
    Works for both sync and async functions. See test below for an example
    """

    def wrapper(*args, **kwargs):
        if len(args) == 1 and callable(args[0]) and not kwargs:
            # The decorator is applied directly without arguments
            return func(args[0])
        else:
            # The decorator is applied with arguments
            def decorator(decorated_func: Callable):
                return func(decorated_func, *args, **kwargs)

            return decorator

    return wrapper


def test():
    @optional_arguments_decorator
    def add_prefix(
        func: Callable,
        prefix: str = "Hello, ",
    ):
        def wrapper(foo: str):
            return func("".join([prefix, foo]))

        return wrapper

    @add_prefix
    def hello(foo: str):
        return foo

    @add_prefix(prefix="Goodbye, ")
    def goodbye(foo: str):
        return foo

    assert hello("foo") == "Hello, foo"
    assert goodbye("foo") == "Goodbye, foo"


if __name__ == "__main__":
    test()
