from typing import Any, Literal, Union


def encode_to_json(value: Any, library: Literal["json", "ujson", "orjson"] = "json", **kwargs) -> Union[str, bytes]:
    """Convert value to JSON.

    Parameters
    ----------
    value: Any
        Value to convert

    library: Literal["json", "ujson"]
        Library to use

    Returnspye
    -------
    str
        JSON value
    """

    if library == "json":
        import json

        return json.dumps(value, **kwargs)
    elif library == "ujson":
        import ujson

        return ujson.dumps(value, **kwargs)
    elif library == "orjson":
        import orjson

        return orjson.dumps(value, **kwargs)


def test():
    assert encode_to_json({"a": 1, "b": 2}, library="json") == '{"a": 1, "b": 2}'
    assert encode_to_json({"a": 1, "b": 2}, library="ujson") == '{"a":1,"b":2}'
    assert encode_to_json({"a": 1, "b": 2}, library="orjson") == b'{"a":1,"b":2}'


if __name__ == "__main__":
    test()
