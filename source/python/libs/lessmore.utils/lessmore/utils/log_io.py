from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Optional

from loguru import logger

from deeplay.utils.loguru_utils import configure_loguru


def log_io(
    input_logger: Optional[Callable] = None,
    output_logger: Optional[Callable] = lambda func, args, kwargs, result: logger.debug(
        func.__name__, args=args, kwargs=kwargs, result=result
    ),
):
    """Decorator to log input and output of a function"""

    def _log_io(func):
        # - Replace input_logger and output_logger with stubs if not provided

        nonlocal input_logger, output_logger

        if not input_logger:
            input_logger = lambda func, args, kwargs: None

        if not output_logger:
            output_logger = lambda func, args, kwargs, result: None

        # - Define decorators

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            input_logger(func=func, args=args, kwargs=kwargs)

            result = await func(*args, **kwargs)

            output_logger(func=func, args=args, kwargs=kwargs, result=result)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            input_logger(func=func, args=args, kwargs=kwargs)

            result = func(*args, **kwargs)

            output_logger(func=func, args=args, kwargs=kwargs, result=result)

            return result

        # - Return the appropriate wrapper

        return async_wrapper if iscoroutinefunction(func) else sync_wrapper

    return _log_io


def test():
    configure_loguru()

    @log_io()
    def example_sync_function(x, y):
        return x + y

    @log_io()
    async def example_async_function(x, y):
        return x + y

    example_sync_function(5, 3)

    import asyncio

    asyncio.run(example_async_function(5, 3))


if __name__ == "__main__":
    test()
