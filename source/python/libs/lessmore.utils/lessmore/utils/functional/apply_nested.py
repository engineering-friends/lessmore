from typing import Any, Callable, Optional, Sequence


def apply_nested(
    value: Any,
    value_func: Callable = lambda x: x,
    key_func: Callable = lambda x: x,
    filter_func: Callable = lambda key, value: True,
    excluded_builtin_types: Sequence = (),
):
    """apply_nested function recursively to python common object types: list, dict, set, tuple"""

    # - Return applied function if not dict, list, set, tuple

    if not isinstance(value, (dict, list, set, tuple)) or (
        excluded_builtin_types and type(value) in excluded_builtin_types
    ):
        return value_func(value)

    # - Apply function to dict, list, set, tuple

    if isinstance(value, dict):
        return {
            key_func(k): apply_nested(
                v,
                value_func=value_func,
                key_func=key_func,
                filter_func=filter_func,
                excluded_builtin_types=excluded_builtin_types,
            )
            for k, v in value.items()
            if filter_func(key=k, value=v)
        }
    else:
        # isinstance(value, (list, set, tuple))
        return type(value)(
            (
                apply_nested(
                    v,
                    value_func=value_func,
                    key_func=key_func,
                    filter_func=filter_func,
                    excluded_builtin_types=excluded_builtin_types,
                )
                for v in value
                if filter_func(key=None, value=v)
            )
        )


def test():
    d = {"d": 3, "b": {"e": [1, 2, 3], "f": {"g": 1}}}

    # - Basic usage

    assert apply_nested(d, value_func=lambda v: None) == {
        "d": None,
        "b": {"e": [None, None, None], "f": {"g": None}},
    }

    # - Exclude types

    assert apply_nested(
        d,
        value_func=lambda value: "this was a list" if isinstance(value, list) else None,
        excluded_builtin_types=[list],
    ) == {
        "d": None,
        "b": {"e": "this was a list", "f": {"g": None}},
    }

    # - Apply_nested to keys

    assert apply_nested(d, key_func=lambda key: key.upper()) == {"D": 3, "B": {"E": [1, 2, 3], "F": {"G": 1}}}

    # - Filter

    assert apply_nested(d, filter_func=lambda key, value: value != 3) == {"b": {"e": [1, 2], "f": {"g": 1}}}


if __name__ == "__main__":
    test()
