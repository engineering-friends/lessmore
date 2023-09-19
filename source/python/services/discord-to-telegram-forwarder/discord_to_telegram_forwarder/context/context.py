from dataclasses import dataclass

from discord_to_telegram_forwarder.config import Config
from loguru import Logger
from telethon import TelegramClient


@dataclass
class Context:
    config: Config
    logger: Logger
    telegram_bot_client: TelegramClient
    telegram_user_client: TelegramClient
