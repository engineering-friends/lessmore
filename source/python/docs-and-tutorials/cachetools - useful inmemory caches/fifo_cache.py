import cachetools


cache = cachetools.FIFOCache(maxsize=2)

for i in range(4):
    cache[i] = i
    print(cache)
