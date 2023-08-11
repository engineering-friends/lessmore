def subtract_dicts(dict1, dict2):
    difference = {}
    for key in dict1:
        if key not in dict2:
            difference[key] = dict1[key]
        elif isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            nested_diff = subtract_dicts(dict1[key], dict2[key])
            if nested_diff:
                difference[key] = nested_diff
        elif dict1[key] != dict2[key]:
            difference[key] = dict1[key]
    return difference


def test():
    assert subtract_dicts({"a": {"b": 2, "c": 3}}, {"a": {"b": 2}}) == {"a": {"c": 3}}
    assert subtract_dicts({"a": {"b": {"c": 3}}}, {"a": {"b": {"c": 4}}}) == {"a": {"b": {"c": 3}}}


if __name__ == "__main__":
    test()
