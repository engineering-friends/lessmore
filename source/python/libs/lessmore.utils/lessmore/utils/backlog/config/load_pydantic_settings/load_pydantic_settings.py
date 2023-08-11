from typing import Optional

from pydantic import BaseSettings

from lessmore.utils.config.load_pydantic_settings._inflate_envs import _inflate_envs
from lessmore.utils.config.read_config import ConfigSourceLike, read_config


def load_pydantic_settings(
    pydantic_class: type[BaseSettings],
    config_source: ConfigSourceLike,
    context: Optional[dict] = None,
) -> BaseSettings:
    """Load pydantic settings from config_source."""

    # todo later: make more elegant solution without using environment variables. For example, use temprorary .env file [@marklidenberg]

    # - Read config

    config = read_config(config_source=config_source, context=context)

    # - Inflate environment variables

    _inflate_envs(config)

    # - Load config

    result = pydantic_class()

    # - Return

    return result


def test():

    from pydantic import BaseSettings

    class Config(BaseSettings):
        a: int
        b: str

    print(
        load_pydantic_settings(
            pydantic_class=Config,
            config_source={
                "type": "dictionary",
                "value": {
                    "a": 1,
                    "b": "foo",
                },
            },
        )
    )


if __name__ == "__main__":
    test()
