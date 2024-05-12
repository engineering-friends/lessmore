import hashlib
import inspect
import json

from functools import lru_cache, wraps

from diskcache import Cache


@lru_cache(maxsize=None)
def cache_on_disk(directory: str = "/tmp/cache_on_disk", reset: bool = False) -> callable:
    """
    Decorator factory that takes a directory name for storing cache data.
    Returns a decorator that caches the results of the function to disk.

    # todo: handle closing the cache or using other library, this is a quick and dirty implementation
    """

    # - Initialize or retrieve an existing cache object

    cache = Cache(directory)

    # - Define the decorator

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # - Generate a unique key based on function arguments and their values

            # -- Get full kwargs

            bound_arguments = inspect.signature(func).bind(*args, **kwargs)
            bound_arguments.apply_defaults()
            full_kwargs = bound_arguments.arguments

            # -- Generate the key

            hasher = hashlib.sha256()
            hasher.update(func.__name__.encode() + json.dumps(full_kwargs, sort_keys=True, default=str).encode())
            key = hasher.hexdigest()

            # - Check if the result is already in the cache

            if key in cache and not reset:
                return cache[key]

            # - Calculate the result if not cached

            result = func(*args, **kwargs)

            # - Store the result in the cache

            cache[key] = result
            return result

        return wrapper

    return decorator


def test():
    def expensive_function(a, b=3, *args, **kwargs):
        return a + b + sum(args) + sum(kwargs.values())

    print(cache_on_disk()(expensive_function)(10, 30, 40, key1=50, key2=60))


if __name__ == "__main__":
    test()
