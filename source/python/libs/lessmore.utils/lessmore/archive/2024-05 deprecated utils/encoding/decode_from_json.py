from typing import Any, Literal, Union


def decode_from_json(value: Union[str, bytes], library: Literal["json", "ujson", "orjson"] = "json", **kwargs) -> Any:
    """Convert value from JSON.

    Parameters
    ----------
    value: Union[str, bytes]
        Value to convert

    library: Literal["json", "ujson"]
        Library to use

    Returns
    -------
    Any
        JSON value
    """

    if library == "json":
        import json

        return json.loads(value, **kwargs)

    elif library == "ujson":
        import ujson

        return ujson.loads(value, **kwargs)

    elif library == "orjson":
        import orjson

        return orjson.loads(value)


def test():
    assert decode_from_json('{"a": 1, "b": 2}', library="json") == {"a": 1, "b": 2}
    assert decode_from_json('{"a":1,"b":2}', library="ujson") == {"a": 1, "b": 2}
    assert decode_from_json(b'{"a":1,"b":2}', library="orjson") == {"a": 1, "b": 2}


if __name__ == "__main__":
    test()
