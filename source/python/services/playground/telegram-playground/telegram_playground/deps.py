from dataclasses import dataclass
from pathlib import Path

from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config
from telegram_playground.config.config import Config


@dataclass
class Deps:
    config: Config

    @staticmethod
    def load(log_level="DEBUG") -> "Deps":
        # - Init logger

        setup_json_loguru(level=log_level)

        # - Return deps

        return Deps(config=Config(**read_config([f"{str(Path(__file__).parent)}/config/config.yaml"])))


if __name__ == "__main__":
    deps = Deps.load()
    print(deps.config)
