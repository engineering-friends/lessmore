import os

from dataclasses import dataclass
from pathlib import Path

import openai

from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config

from youtube_transcripts.config.config import Config


@dataclass
class Deps:
    config: Config

    @staticmethod
    def load(log_level="DEBUG") -> "Deps":
        # - Init config

        config = Config(**read_config([f"{str(Path(__file__).parent)}/config/config.yaml"]))

        # - Init logger

        setup_json_loguru(level=log_level)

        # - Return deps

        return Deps(config=config)


def test():
    print(Deps.load().config)


if __name__ == "__main__":
    test()
