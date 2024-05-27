import os.path

from typing import Union

import anyconfig
import requests

from dotenv import load_dotenv

from lessmore.utils.file_primitives.write_file import write_file
from lessmore.utils.read_config.merge_dicts import merge_dicts
from lessmore.utils.read_config.resolve_placeholders import resolve_placeholders


SUPPORTED_EXTENSIONS = [".json", ".yaml"]

ENV = "env"


def read_config(
    source: Union[str, dict, list, ENV],
) -> dict:
    """Read config from multiple sources, merge them and replace placeholders at the end of the process from the config itself.

    Parameters
    ----------
    source: Union[str, dict, list]
        Config source. Can be a filename/url/"env", dictionary or list of sources
    """

    # - Get config

    if isinstance(source, list):
        # - Read sub configs. Context is a cumulative config

        result = merge_dicts([read_config(_source) for _source in source])

    elif isinstance(source, dict):
        result = source
    elif isinstance(source, str):
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

    result = resolve_placeholders(result)

    # - Return result

    return result


def test():
    write_file(data="a: 1\nb: '{a}'", filename="/tmp/test.yaml")
    write_file(data='{"a": 10}', filename="/tmp/test.json")

    print(read_config(["/tmp/test.yaml", "/tmp/test.json"]))


if __name__ == "__main__":
    test()
