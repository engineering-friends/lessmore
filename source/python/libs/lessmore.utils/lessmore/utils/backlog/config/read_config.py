import os.path

from functools import reduce
from typing import Any, Dict, List, Mapping, Optional, Union

import requests

from lessmore.utils.coder import decode_yaml
from lessmore.utils.config.read_config_file import read_config_file
from lessmore.utils.dictionary import merge_dicts


SUPPORTED_EXTENSIONS = [".env", ".json", ".yaml"]


ConfigSourceLike = Union[str, Dict, List]


def read_config(
    config_source: ConfigSourceLike,
    context: Optional[dict] = None,
) -> dict:
    """Read config from config_source

    Parameters
    ----------
    config_source : ConfigSourceLike
        Config source
    context : Optional[dict]
        Current context. Will be used to resolve config_source if it is a filename
    """

    # - Prepare arguments

    context = context or {}

    # - Get config

    result = None

    if isinstance(config_source, list):

        # - Read sub configs. Context is a cumulative config

        result = reduce(
            lambda config, sub_config_source: merge_dicts(
                [config, read_config(sub_config_source, context=config)]
            ),
            [context] + config_source,
        )

    elif isinstance(config_source, dict):

        # value: {'value': <config_like>, 'is_optional': bool, 'type'}
        assert set(config_source.keys()).issubset({"type", "is_required", "value", "prefix"})
        assert config_source["type"] in ["file", "dictionary", "environment_variables", "url"]

        if config_source["type"] == "file":

            # - Fill kwargs to path

            config_source["value"] = config_source["value"].format(**context)

            # - Normalize path

            config_source["value"] = os.path.abspath(config_source["value"])

            # - Read config file if needed

            if not config_source.get("is_required") and not os.path.exists(config_source["value"]):
                result = {}
            else:
                result = read_config_file(config_source["value"])

        elif config_source["type"] == "dictionary":
            result = config_source["value"]

        elif config_source["type"] == "environment_variables":
            result = dict(os.environ)
        elif config_source["type"] == "url":
            result = decode_yaml(requests.get(config_source["value"]).text)

        # - Fix None type if needed

        result = result or {}

        # - Make all config keys lowercase

        result = {k.lower(): v for k, v in result.items()}

        # - Filter prefix if needed

        if "prefix" in config_source:
            result = {k: v for k, v in result.items() if k.startswith(config_source["prefix"].lower())}
            result = {k[len(config_source["prefix"]) :]: v for k, v in result.items()}

    elif isinstance(config_source, str):
        if config_source == "environment_variables":
            return dict(os.environ)
        else:

            # - Fill kwargs to path

            config_source = config_source.format(**context)

            # - Normalize path

            config_source = os.path.abspath(config_source)

            # - Read config file

            result = read_config_file(config_source)

    return result


def test():
    with open("/tmp/test.yaml", "w") as file:
        file.write("a: 1\nb: 2")

    assert read_config([{"type": "dictionary", "value": {"a": 1, "b": 2}}]) == {"a": 1, "b": 2}
    assert read_config([{"type": "file", "value": "/tmp/test.yaml"}]) == {"a": 1, "b": 2}
    assert read_config([{"type": "file", "value": "/tmp/non_existent.yaml", "is_required": False}]) == {}

    print(
        "Url config",
        read_config(
            {
                "type": "url",
                "value": "https://raw.githubusercontent.com/codefresh-io/yaml-examples/master/codefresh-build-1.yml",
            }
        ),
    )

    # list config

    assert read_config(
        [
            {"type": "dictionary", "value": {"a": 1, "b": 2}},
            {"type": "dictionary", "value": {"b": 3, "c": 4}},
        ]
    ) == {"a": 1, "b": 3, "c": 4}


if __name__ == "__main__":
    test()
