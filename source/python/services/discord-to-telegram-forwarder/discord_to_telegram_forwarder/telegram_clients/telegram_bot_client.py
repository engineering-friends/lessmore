from pathlib import Path

from discord_to_telegram_forwarder.config.config import config
from telethon import TelegramClient


telegram_bot_client = TelegramClient(
    session=str(Path(__file__).parent / "telegram_bot.session"),
    api_id=int(config.telegram_api_id),
    api_hash=config.telegram_api_hash,
)
