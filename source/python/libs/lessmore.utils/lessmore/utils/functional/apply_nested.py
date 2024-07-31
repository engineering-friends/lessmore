from typing import Any, Callable, Optional, Sequence


def apply_nested(
    value: Any,
    func: Callable = lambda key, value: (key, value),
    filter_func: Callable = lambda key, value: True,
    excluded_builtin_types: Sequence = (),
) -> Any:
    """Apply function recursively to python nested object types: list, dict, set, tuple"""

    # - Return applied function if not dict, list, set, tuple

    if not isinstance(value, (dict, list, set, tuple)) or (
        excluded_builtin_types and type(value) in excluded_builtin_types
    ):
        return func(key="", value=value)[1]

    # - Apply function to dict, list, set, tuple

    if isinstance(value, dict):
        result = {}

        for k, v in value.items():
            if not filter_func(key=k, value=v):
                continue

            if isinstance(v, (dict, list, set, tuple)):
                result[func(key=k, value=None)[0]] = apply_nested(
                    v,
                    func=func,
                    filter_func=filter_func,
                    excluded_builtin_types=excluded_builtin_types,
                )
            else:
                _k, _v = func(k, v)
                result[_k] = _v

        return result
    else:
        # isinstance(value, (list, set, tuple))
        return type(value)(
            (
                apply_nested(
                    v,
                    func=func,
                    filter_func=filter_func,
                    excluded_builtin_types=excluded_builtin_types,
                )
                for v in value
                if filter_func(key="", value=v)
            )
        )


def test():
    d = {"d": 3, "b": {"e": [1, 2, 3], "f": {"g": 1}}}

    # - Basic usage

    assert apply_nested(d, func=lambda key, value: (key, None)) == {
        "d": None,
        "b": {"e": [None, None, None], "f": {"g": None}},
    }

    # - Exclude types

    assert apply_nested(
        d,
        func=lambda key, value: (key, "this was a list" if isinstance(value, list) else None),
        excluded_builtin_types=[list],
    ) == {
        "d": None,
        "b": {"e": "this was a list", "f": {"g": None}},
    }

    # - Apply_nested to keys

    assert apply_nested(d, func=lambda key, value: (key.upper(), value)) == {
        "D": 3,
        "B": {"E": [1, 2, 3], "F": {"G": 1}},
    }

    # - Filter

    assert apply_nested(d, filter_func=lambda key, value: value != 3) == {"b": {"e": [1, 2], "f": {"g": 1}}}


if __name__ == "__main__":
    test()
