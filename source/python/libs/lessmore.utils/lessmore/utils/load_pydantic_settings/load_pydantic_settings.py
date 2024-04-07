from typing import Any, Optional, Type

from pydantic_settings import BaseSettings

from lessmore.utils.load_pydantic_settings.config_source_like import ConfigSourceLike
from lessmore.utils.load_pydantic_settings.inflate_envs import inflate_envs
from lessmore.utils.load_pydantic_settings.load_config_source.load_config_source import load_config_source


def load_pydantic_settings(
    pydantic_class: Any,
    config_source: ConfigSourceLike,
    context: Optional[dict] = None,
) -> Any:
    """Load pydantic settings from config_source."""

    # todo later: make more elegant solution without using environment variables. For example, use temprorary .env file [@marklidenberg]

    # - Read config

    config = load_config_source(config_source=config_source, context=context)

    # - Inflate environment variables

    inflate_envs(envs_by_name=config)

    # - Load config

    result = pydantic_class()

    # - Return

    return result


def test():
    from pydantic import BaseSettings

    class Config(BaseSettings):
        a: int
        b: str

    assert load_pydantic_settings(
        pydantic_class=Config,
        config_source={
            "type": "dictionary",
            "value": {
                "a": 1,
                "b": "foo",
            },
        },
    ) == {"a": 1, "b": "foo"}


if __name__ == "__main__":
    test()
