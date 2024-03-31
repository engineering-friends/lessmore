from dataclasses import dataclass

from second_sun.config.config import Config


@dataclass
class Deps:
    config: Config
