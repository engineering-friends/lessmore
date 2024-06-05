from dataclasses import dataclass

from palette.config.config import Config


@dataclass
class Deps:
    config: Config
