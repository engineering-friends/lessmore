from asyncio import iscoroutinefunction
from typing import Callable, Coroutine, Union


def asyncify(func: Union[Callable, Coroutine]) -> Callable:
    """Decorator to make a function asynchronous.

    Parameters
    ----------
    func : callable
        The function to be made asynchronous.

    Returns
    -------
    callable
        The asynchronous version of the function.
    """

    async def wrapper(*args, **kwargs):
        if iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)

    return wrapper
