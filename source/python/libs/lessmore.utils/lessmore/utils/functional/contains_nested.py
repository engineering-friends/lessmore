from typing import Any, Union


def contains_nested(
    whole: Union[list, dict, str, int, Any],
    part: Union[list, dict, str, int, Any],
) -> bool:
    """Checks if the whole contains the part. The part can be a nested structure."""
    if isinstance(whole, dict) and isinstance(part, dict):
        for key in part:
            if key not in whole:
                return False
            if not contains_nested(whole[key], part[key]):
                return False
        return True
    elif isinstance(whole, list) and isinstance(part, list):
        if len(whole) < len(part):
            return False
        for value in part:
            if not any(contains_nested(element, value) for element in whole):  # brute force search
                # todo maybe: optimize search somehow [@marklidenberg]
                return False
        return True
    else:
        return whole == part


def test():
    assert contains_nested(
        whole={"a": 1, "b": ["foo", "bar", {"c": ["x", "y", "z"]}]},
        part={"a": 1, "b": ["foo", {"c": ["z"]}]},
    )
    assert not contains_nested({"a": 1}, {"b": 2})


if __name__ == "__main__":
    test()
