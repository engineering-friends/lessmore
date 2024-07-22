import os

from dataclasses import dataclass
from pathlib import Path

import openai

from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config

from learn_language_magic.config.config import Config


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

        # - Set amazon keys

        os.environ["AWS_ACCESS_KEY_ID"] = config.aws_access_key_id
        os.environ["AWS_SECRET_ACCESS_KEY"] = config.aws_secret_access_key
        os.environ["AWS_DEFAULT_REGION"] = config.aws_default_region

        # - Return deps

        return Deps(config=config)


def test():
    print(Deps.load().config)


if __name__ == "__main__":
    test()
