import json
import time

from typing import Any, Callable


def run_cached(
    func: Callable,
    args: list = [],
    kwargs: dict = {},
    version: str = "",
    key: str = "",
    reset_condition: Callable = lambda prev_version, prev_timestamp, prev_value, version: prev_version != version,
    cache: dict = {},
    ttl: int = 60 * 60 * 24,
) -> Any:
    # - Clean cache by ttl

    if ttl:
        for k, (_, timestamp, _) in list(cache.items()):
            if (time.time() - timestamp) > ttl:
                del cache[k]

    # - Get map key

    map_key = json.dumps({"key": key or func.__name__, "args": args, "kwargs": kwargs}, sort_keys=True)

    # - Get prev version and value

    prev_version, prev_timestamp, prev_value = cache.get(map_key, (None, None, None))

    # - Calculate function or take from cache

    if map_key not in cache or reset_condition(
        prev_version=prev_version,
        prev_value=prev_value,
        prev_timestamp=prev_timestamp,
        version=version,
    ):
        res = func(*args, **kwargs)
    else:
        res = prev_value

    # - Save to cache with new values

    cache[map_key] = (version, time.time(), res)

    # - Clean old values

    return res


def test():
    cache = {}

    def calculate(value):
        print(f"Calculating {value}...")
        return value * 2

    run_cached(
        calculate,
        kwargs={"value": 1},
        version="1",
        cache=cache,
    )
    run_cached(
        calculate,
        kwargs={"value": 1},
        version="1",
        cache=cache,
    )
    run_cached(
        calculate,
        kwargs={"value": 1},
        version="2",
        cache=cache,
    )

    print(cache)


if __name__ == "__main__":
    test()
