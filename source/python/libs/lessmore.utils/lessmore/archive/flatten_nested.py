from typing import Any

from lessmore.utils.dictionary.recursive_default_dictionary import recursive_defaultdict


def flatten_nested(value: Any, separator: str = ".") -> Any:
    """
    Flatten nested

    Creates a linear representation of a nested dict (some kind of materialized path).
    Separator is used to join dictionary keys / list indexes.

        Notes:
            - function consider numeric item as a list index, and string item as a dictionary key;
            - function in encoders process list only with string items.

        Input:
            {
                'key1': 'value1',
                'key2': ['list_value1', 'list_value2'],
                'key3': {
                    'nested_key1': 1,
                    'nested_key2': 2
                }
            }

        Output:
            {
                'key1': 'value1',
                'key2.0': 'list_value1',
                'key2.1': 'list_value2',
                'key3.nested_key1': 1,
                'key3.nested_key2': 2
            }


    TODO: Add support for list with complex items like dict, list, etc.

        Input:
            {
                'key4': [
                    {'list_sub_key1': 'list_sub_value1'},
                    {'list_sub_key2': 'list_sub_value2'}
                ]
            }

        Output:
            {
                'key4.0.list_sub_key1': 'list_sub_value1',
                'key4.1.list_sub_key2': 'list_sub_value2'
            }
    """

    def _to_iterable(_value):
        if isinstance(_value, list):
            return enumerate(_value)
        elif isinstance(_value, dict):
            return _value.items()

    iter_value = _to_iterable(value)

    if iter_value is not None:
        result = {}

        for k, v in iter_value:
            v_flattened = flatten_nested(v, separator=separator)
            iter_v_flattened = _to_iterable(v_flattened)

            if iter_v_flattened is not None:
                for k1, v1 in iter_v_flattened:
                    result[separator.join([str(k), str(k1)])] = v1

            else:
                result[str(k)] = v_flattened
        return result
    else:
        return value


def unflatten_nested(value, separator="."):
    result = recursive_defaultdict(separator=separator)
    for k, v in value.items():
        result.set_dotted(k, v)
    return result.to_dict()


def test():
    value = {"a": "b", "c": {"d": {"e": "f"}, "g": "h"}}
    assert flatten_nested(value) == {"a": "b", "c.d.e": "f", "c.g": "h"}
    assert unflatten_nested(value) == {"a": "b", "c": {"d": {"e": "f"}, "g": "h"}}

    value = {"a": "b", "c": {"d": {"e": "f"}, "g": "h"}, "p": ["ABC", "bc", {"a": "b"}]}
    assert flatten_nested(value) == {"a": "b", "c.d.e": "f", "c.g": "h", "p.0": "ABC", "p.1": "bc", "p.2.a": "b"}
    assert unflatten_nested(value) == {"a": "b", "c": {"d": {"e": "f"}, "g": "h"}, "p": ["ABC", "bc", {"a": "b"}]}

    value = {"a": "b", "c": {"d": {"e": "f"}, "g": ["h"]}}
    assert flatten_nested(value) == {"a": "b", "c.d.e": "f", "c.g.0": "h"}
    assert unflatten_nested(value) == {"a": "b", "c": {"d": {"e": "f"}, "g": ["h"]}}


if __name__ == "__main__":
    test()
