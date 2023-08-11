from discord_to_telegram_forwarder.config.config import config
from telethon import TelegramClient

from lessmore.utils.path_helpers.get_current_dir import get_current_dir


# - Init client

telegram_client = TelegramClient(
    session=str(get_current_dir() / "telegram.session"),
    api_id=int(config.telegram_api_id),
    api_hash=config.telegram_api_hash,
)
