import os
import sys

from pathlib import Path

import openai

from langchain_playground.config.config import Config
from langchain_playground.deps.deps import Deps
from loguru import logger

from lessmore.utils.configure_loguru.format_as_json_colored.format_as_json_colored import format_as_json_colored
from lessmore.utils.load_pydantic_settings.load_pydantic_settings import load_pydantic_settings


def init_deps(log_level="DEBUG") -> Deps:
    # - Init config

    config = load_pydantic_settings(
        pydantic_class=Config,
        config_source=[
            {
                "type": "file",
                "is_required": False,
                "value": "{root}/config.secrets.yaml",
            },
            # "environment_variables",
        ],
        context={
            "root": str(Path(__file__).parent / "../config"),
        },
    )
    # - Init logger

    logger.remove()
    logger.add(sink=sys.stdout, level=log_level, format=format_as_json_colored)

    # - Set langchain

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = config.langchain_api_key

    # - Set openai key

    openai.api_key = config.openai_api_key

    # - Return deps

    return Deps(config=config)


def test():
    print(init_deps())


if __name__ == "__main__":
    test()
