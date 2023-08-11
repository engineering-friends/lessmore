from typing import Any, Callable, Optional


def recursive_apply(
    value: Any,
    value_func: Callable = lambda x: x,
    key_func: Callable = lambda x: x,
    filter_func: Optional[Callable] = None,
    excluded_builtin_types: Optional[list] = None,
    *args,
    **kwargs,
):
    """Apply function recursively to python common object types: list, dict, set, tuple"""

    # - Init input arguments

    value_func = value_func or (lambda x: x)
    key_func = key_func or (lambda x: x)
    filter_func = filter_func or (lambda key, value: True)

    # - Return applied function if not dict, list, set, tuple

    if not isinstance(value, (dict, list, set, tuple)):
        return value_func(value, *args, **kwargs)

    if excluded_builtin_types and type(value) in excluded_builtin_types:
        return value_func(value, *args, **kwargs)

    if isinstance(value, dict):
        return {
            key_func(k): recursive_apply(
                v,
                value_func=value_func,
                key_func=key_func,
                filter_func=filter_func,
                excluded_builtin_types=excluded_builtin_types,
                *args,
                **kwargs,
            )
            for k, v in value.items()
            if filter_func(key=k, value=v)
        }
    elif isinstance(value, list):
        return [
            recursive_apply(
                v,
                value_func=value_func,
                key_func=key_func,
                filter_func=filter_func,
                excluded_builtin_types=excluded_builtin_types,
                *args,
                **kwargs,
            )
            for v in value
            if filter_func(key=None, value=v)
        ]
    elif isinstance(value, set):
        return {
            recursive_apply(
                v,
                value_func=value_func,
                key_func=key_func,
                filter_func=filter_func,
                excluded_builtin_types=excluded_builtin_types,
                *args,
                **kwargs,
            )
            for v in value
            if filter_func(key=None, value=v)
        }
    elif isinstance(value, tuple):
        return tuple(
            recursive_apply(
                v,
                value_func=value_func,
                key_func=key_func,
                filter_func=filter_func,
                excluded_builtin_types=excluded_builtin_types,
                *args,
                **kwargs,
            )
            for v in value
            if filter_func(key=None, value=v)
        )
    else:
        return value_func(value, *args, **kwargs)


def test():
    d = {"d": 3, "b": {"e": [1, 2, 3], "f": {"g": 1}}}

    # - Basic usage

    assert recursive_apply(d, value_func=lambda v: None) == {
        "d": None,
        "b": {"e": [None, None, None], "f": {"g": None}},
    }

    # - Exclude types

    assert recursive_apply(
        d,
        value_func=lambda value: "this was a list" if isinstance(value, list) else None,
        excluded_builtin_types=[list],
    ) == {
        "d": None,
        "b": {"e": "this was a list", "f": {"g": None}},
    }

    # - Apply to keys

    assert recursive_apply(d, key_func=lambda key: key.upper()) == {"D": 3, "B": {"E": [1, 2, 3], "F": {"G": 1}}}

    # - Filter

    assert recursive_apply(d, filter_func=lambda key, value: value != 3) == {"b": {"e": [1, 2], "f": {"g": 1}}}


if __name__ == "__main__":
    test()
