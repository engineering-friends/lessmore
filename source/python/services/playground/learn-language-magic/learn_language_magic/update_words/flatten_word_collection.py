def flatten_word_collection(collection: dict, prefix: str = "") -> dict:
    result = {}
    for key, value in collection.items():
        if isinstance(value, dict):
            result.update(flatten_word_collection(value, prefix + key + "::"))
        else:
            result[prefix + key] = value
    return result


def test():
    collection = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    print(flatten_word_collection(collection))


if __name__ == "__main__":
    test()
