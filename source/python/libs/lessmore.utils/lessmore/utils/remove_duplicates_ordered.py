def remove_duplicates_ordered(values, key=None):
    # preserves order of sequence
    seen = set()
    seen_add = seen.add
    key = key or (lambda x: x)
    return [x for x in values if not (key(x) in seen or seen_add(key(x)))]


def test():
    assert remove_duplicates_ordered([2, 2, 1, 1, 3, 3]) == [2, 1, 3]


if __name__ == "__main__":
    test()
