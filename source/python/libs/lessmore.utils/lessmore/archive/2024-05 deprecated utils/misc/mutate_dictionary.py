from typing import Callable, Dict, List, Union

from lessmore.utils.dictionary import merge_dicts


def mutate_dictionary(value: dict, mutation: Union[Callable, dict]):
    if callable(mutation):
        mutation = mutation(value)
    return merge_dicts([value, mutation])


def test():
    assert mutate_dictionary({"a": 1, "b": {"c": 1}}, mutation=lambda value: {"mutated": True, "b": {"c": 2}}) == {
        "a": 1,
        "b": {"c": 2},
        "mutated": True,
    }
    assert mutate_dictionary({"a": 1, "b": {"c": 1}}, mutation={"mutated": True, "b": {"c": 2}}) == {
        "a": 1,
        "b": {"c": 2},
        "mutated": True,
    }


if __name__ == "__main__":
    test()
