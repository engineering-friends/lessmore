import os

from dataclasses import dataclass
from pathlib import Path

import openai

from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config
from teletalk.test_deps.config.config import Config


@dataclass
class TestDeps:
    config: Config

    @staticmethod
    def load(log_level="DEBUG") -> "Deps":
        # - Setup loguru

        setup_json_loguru(level=log_level)

        # - Init config

        config = Config(**read_config([f"{str(Path(__file__).parent)}/config/config.yaml"]))

        # - Return deps

        return TestDeps(config=config)


def test():
    print(TestDeps.load().config)


if __name__ == "__main__":
    test()
