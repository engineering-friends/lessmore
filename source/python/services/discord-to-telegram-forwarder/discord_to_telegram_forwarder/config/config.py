from typing import Union

from pydantic import BaseSettings
from enum import Enum
from typing import Dict, Union
from pydantic import BaseSettings


class EmojiPack(Enum):
    MINIMAL = "minimal"
    CORE = "core"
    ALL = "all"


class EmojiUserConfig(BaseSettings):
    emoji_count: int
    emoji_pack: EmojiPack


class Config(BaseSettings):
    # - Telegram

    telegram_api_id: str
    telegram_api_hash: str
    telegram_bot_name: str
    telegram_bot_token: str
    telegram_ef_discussions: Union[int, str]
    telegram_ef_channel: Union[int, str]

    # - Discord

    discord_token: str
    guild_name: str

    # - OpenAI

    openai_api_key: str

    # - Emoji Config

    emoji_config: Dict[str, EmojiUserConfig] = {
        "Mark Lidenberg": {"emoji_count": 1, "emoji_pack": EmojiPack.MINIMAL},
        "Petr Lavrov": {"emoji_count": 5, "emoji_pack": EmojiPack.ALL},
        "Mikhail Vodolagin": {"emoji_count": 3, "emoji_pack": EmojiPack.CORE},
        "default": {"emoji_count": 1, "emoji_pack": EmojiPack.CORE},
    }
