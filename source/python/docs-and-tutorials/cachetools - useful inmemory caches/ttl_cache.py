import time

import cachetools


ttl_cache = cachetools.TTLCache(
    maxsize=1_000_000,
    ttl=1,  # seconds
)


ttl_cache["a"] = 1
ttl_cache["b"] = 2
ttl_cache["c"] = 3
ttl_cache["d"] = 4

assert dict(ttl_cache) == {"a": 1, "b": 2, "c": 3, "d": 4}

time.sleep(1)
ttl_cache["e"] = 5
time.sleep(0.5)

assert dict(ttl_cache) == {"e": 5}
