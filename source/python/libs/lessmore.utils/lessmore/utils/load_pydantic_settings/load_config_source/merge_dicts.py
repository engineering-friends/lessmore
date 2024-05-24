import collections.abc

from typing import Dict, List


# NOTE: use anyconfig.merge for more advanced merge logics
def merge_dicts(values: List[Dict]):
    """Merge dictionaries

    Parameters
    ----------
    values : List[Dict]
        List of dictionaries to merge

    Returns
    -------
    Dict
        Merged dictionary

    Examples
    --------
    >>> merge_dicts([{"a": 1}, {"a": {"b": 2}}, {"a": {"c": 3}}])
    {'a': {'b': 2, 'c': 3}}

    """
    result = values[0]
    for value in values[1:]:
        for k, v in value.items():
            if isinstance(v, collections.abc.Mapping):
                result_subvalue = result.get(k, {})
                if isinstance(result_subvalue, collections.abc.Mapping):
                    result[k] = merge_dicts([result.get(k, {}), v])
                else:
                    result[k] = v
            else:
                result[k] = value[k]
    return result


def test():
    assert merge_dicts([{"a": 1}, {"a": {"b": 2}}, {"a": {"c": 3}}]) == {"a": {"b": 2, "c": 3}}


if __name__ == "__main__":
    test()
