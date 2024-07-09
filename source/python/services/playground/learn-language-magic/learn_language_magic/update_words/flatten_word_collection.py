def flatten_word_collection(collection: dict, prefix: str = "") -> dict:
    result = {}
    for key, value in collection.items():
        if isinstance(value, dict):
            result.update(flatten_word_collection(value, prefix + key + "::"))
        else:
            result[prefix + key] = value
    return result


def test():
    assert flatten_word_collection({"a": 1, "b": {"c": 2, "d": {"e": 3}}}) == {"a": 1, "b::c": 2, "b::d::e": 3}


if __name__ == "__main__":
    test()
