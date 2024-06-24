import os
import sys

from dataclasses import dataclass
from pathlib import Path

import openai

from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config

from palette.config.config import Config


@dataclass
class Deps:
    config: Config

    @staticmethod
    def load(log_level="DEBUG") -> "Deps":
        # - Init config

        config = Config(**read_config([f"{str(Path(__file__).parent)}/config/config.yaml"]))

        # - Init logger

        setup_json_loguru(level=log_level)

        # - Set langchain

        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = config.langchain_api_key

        # - Set openai key

        openai.api_key = config.openai_api_key

        # - Return deps

        return Deps(config=config)


def test():
    print(Deps.load())


if __name__ == "__main__":
    test()
