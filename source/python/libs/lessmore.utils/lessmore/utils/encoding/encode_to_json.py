from typing import Any, Literal


def encode_to_json(value: Any, library: Literal["json", "ujson", "orjson"]) -> str | bytes:
    """Convert value to JSON.

    Parameters
    ----------
    value: Any
        Value to convert

    library: Literal["json", "ujson"]
        Library to use

    Returns
    -------
    str
        JSON value
    """
    return json.dumps(value)
