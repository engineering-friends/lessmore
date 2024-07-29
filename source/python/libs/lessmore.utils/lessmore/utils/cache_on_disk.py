import asyncio
import hashlib
import inspect
import json

from functools import lru_cache, wraps

from diskcache import Cache

from lessmore.utils.file_primitives.ensure_path import ensure_path


@lru_cache(maxsize=None)
def cache_on_disk(
    directory: str = "/tmp/cache_on_disk",
    reset: bool = False,
) -> callable:
    """
    Decorator factory for caching the results of a function to disk.

    # todo later: handle closing the cache or using other library, this is a quick and dirty implementation [@marklidenberg]
    """

    # - Initialize or retrieve an existing cache object

    cache = Cache(ensure_path(directory))

    # - Define the decorator

    def _get_key(func, args, kwargs):
        # - Generate a unique key based on function arguments and their values

        # -- Get full kwargs

        bound_arguments = inspect.signature(func).bind(*args, **kwargs)
        bound_arguments.apply_defaults()
        full_kwargs = bound_arguments.arguments

        # -- Generate the key

        hasher = hashlib.sha256()

        # Include function name in the hash
        hasher.update(func.__name__.encode())

        # Function to convert arguments to a hashable form
        def hashable(arg):
            if callable(arg):  # Check if the argument is callable (e.g., a lambda function)
                try:
                    source = inspect.getsource(arg).strip()
                    hasher.update(source.encode())
                except (TypeError, OSError):  # If the source can't be retrieved
                    hasher.update(str(id(arg)).encode())  # Use the memory address as a fallback
            else:
                hasher.update(json.dumps(arg, sort_keys=True, default=str).encode())

        # Convert arguments and keyword arguments to a hashable form
        for key, value in full_kwargs.items():
            hasher.update(key.encode())
            hashable(value)

        return hasher.hexdigest()

    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # - Get key

            key = _get_key(func=func, args=args, kwargs=kwargs)

            # - Check if the result is already in the cache

            if key in cache and not reset:
                return cache[key]

            # - Calculate the result if not cached

            result = func(*args, **kwargs)

            # - Store the result in the cache

            cache[key] = result
            return result

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # - Get key

            key = _get_key(func=func, args=args, kwargs=kwargs)

            # - Check if the result is already in the cache

            if key in cache and not reset:
                return cache[key]

            # - Calculate the result if not cached

            result = await func(*args, **kwargs)

            # - Store the result in the cache

            cache[key] = result
            return result

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def test():
    def expensive_function(a, b=3, *args, **kwargs):
        return a + b + sum(args) + sum(kwargs.values())

    async def async_expensive_function(a, b=3, *args, **kwargs):
        await asyncio.sleep(1)
        return a + b + sum(args) + sum(kwargs.values())

    print(cache_on_disk()(expensive_function)(10, 30, 40, key1=50, key2=60))

    async def test_async():
        print(await cache_on_disk()(async_expensive_function)(10, 30, 40, key1=50, key2=60))

    asyncio.run(test_async())


if __name__ == "__main__":
    test()
