from typing import Any, Literal, Union


def decode_from_yaml(value: str) -> Any:
    """Convert value from YAML.

    Parameters
    ----------
    value: str
        Value to convert

    Returns
    -------
    Any
        YAML value
    """

    import yaml

    return yaml.safe_load(value)


def test():
    assert decode_from_yaml('{"a": 1, "b": 2}') == {"a": 1, "b": 2}


if __name__ == "__main__":
    test()
