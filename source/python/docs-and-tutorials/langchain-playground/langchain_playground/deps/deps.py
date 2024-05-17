from dataclasses import dataclass

from discord_to_telegram_forwarder.config.config import Config


@dataclass
class Deps:
    config: Config
