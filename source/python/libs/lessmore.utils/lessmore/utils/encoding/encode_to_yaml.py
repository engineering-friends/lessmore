from typing import Any, Literal, Union

from inline_snapshot import snapshot

from lessmore.utils.backlog.run_inline_snapshot_tests import run_inline_snapshot_tests


def encode_to_yaml(value: Any, **kwargs) -> str:
    """Convert value to YAML.

    Parameters
    ----------
    value: Any
        Value to convert

    Returns
    -------
    Union[str, bytes]
        YAML value
    """

    import yaml

    kwargs.setdefault("sort_keys", False)
    kwargs.setdefault("default_flow_style", False)
    kwargs.setdefault("allow_unicode", True)
    return yaml.dump(value, **kwargs)


def test():
    assert encode_to_yaml({"a": 1, "b": 2}) == snapshot("a: 1\nb: 2\n")


if __name__ == "__main__":
    # run_inline_snapshot_tests()
    test()
