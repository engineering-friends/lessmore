import os.path

from typing import Union

import anyconfig
import requests

from dotenv import load_dotenv
from lessmore.utils.file_primitives.write_file import write_file
from lessmore.utils.read_config.merge_dicts import merge_dicts
from lessmore.utils.read_config.resolve_dict_placeholders import resolve_dict_placeholders
from lessmore.utils.read_config.resolve_str_placeholders import resolve_str_placeholders


SUPPORTED_EXTENSIONS = [".json", ".yaml"]

ENV = "env"


def read_config(
    source: Union[str, dict, list, ENV],
    _cumulative_config: dict = {},
) -> dict:
    """Read config from multiple sources (dictionaries/files/urls/environment variables), merge them and replace templated placeholders at the end of the process from the config itself.

    Useful when you have a root config with environment key (e.g. "test", "prod") and you want to read and merge another config with separate file for each environment.

    Parameters
    ----------
    source: Union[str, dict, list]
        Config source. Can be a filename/url/"env", dictionary or list of sources
    """

    # - Get config

    if isinstance(source, list):
        # - Read sub configs. Context is a cumulative config

        _cumulative_config = {}

        for _source in source:
            new_config = read_config(source=_source, _cumulative_config=_cumulative_config)
            _cumulative_config = merge_dicts([_cumulative_config, new_config])

        result = _cumulative_config

    elif isinstance(source, dict):
        result = source
    elif isinstance(source, str):
        # - Try to resolve placeholders in string (e.g. 'foo {bar} baz {qux}', {"bar": 1} -> 'foo 1 baz {qux}')

        source = resolve_str_placeholders(source, context=_cumulative_config)

        # - Load config

        if source == "env":
            load_dotenv()
            result = dict(os.environ)
        elif os.path.exists(source):
            # filename
            result = anyconfig.load(os.path.abspath(source))
        elif source.startswith("http"):
            # download locally
            write_file("/tmp/config.yaml", requests.get(source).text)
            result = anyconfig.load("/tmp/config.yaml")
        else:
            raise ValueError(f"Config not found: {type(source)}")
    else:
        raise ValueError(f"Unexpected source type: {type(source)}")

    # - Resolve placeholders for all strings in the config

    result = resolve_dict_placeholders(result)

    # - Return result

    return result


def test():
    write_file(data="a: 1\nb: '{a}'\nenvironment: test", filename="/tmp/test.yaml")
    write_file(data='{"c": 10}', filename="/tmp/test.json")
    assert read_config(["/tmp/test.yaml", "/tmp/{environment}.json"]) == {
        "a": 1,
        "b": "1",
        "environment": "test",
        "c": 10,
    }


if __name__ == "__main__":
    test()
