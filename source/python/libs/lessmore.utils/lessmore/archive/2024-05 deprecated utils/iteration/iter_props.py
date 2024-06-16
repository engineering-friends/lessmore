import itertools


def _iter_key(properties, key):
    for v in properties[key]:
        yield key, v


def iter_props(properties):
    iterators = [_iter_key(properties, k) for k in properties]
    for combo in itertools.product(*iterators):
        yield dict(combo)


def test():
    properties = {"a": [1, 2, 3], "b": [0, 1]}
    print(list(iter_props(properties)))


if __name__ == "__main__":
    test()
