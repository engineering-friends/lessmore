from dataclasses import dataclass

from discord_to_telegram_forwarder.config.config import Config
from telethon import TelegramClient


@dataclass
class Deps:
    config: Config
    cache: dict
    local_files_dir: str
    telegram_bot_client: TelegramClient
    telegram_user_client: TelegramClient
