from typing import Union

from pydantic import BaseSettings


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

    # - Telegram and discord

    telegram_username_to_discord_aliases_json: str = "{}"

    # - OpenAI

    openai_api_key: str

    # - App

    filter_public_channels: bool = True
