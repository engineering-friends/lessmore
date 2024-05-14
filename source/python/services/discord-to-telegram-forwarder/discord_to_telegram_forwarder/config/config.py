from typing import Union

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # - Telegram

    telegram_api_id: str
    telegram_api_hash: str
    telegram_bot_name: str
    telegram_bot_token: str
    telegram_ef_discussions: Union[int, str]
    telegram_ef_channel: Union[int, str]

    @field_validator("telegram_ef_discussions", mode="before")
    @classmethod
    def convert_telegram_ef_discussions(cls, telegram_ef_discussions: Union[int, str]):
        try:
            return int(telegram_ef_discussions)
        except:
            return telegram_ef_discussions

    @field_validator("telegram_ef_channel", mode="before")
    @classmethod
    def convert_telegram_ef_channel(cls, telegram_ef_discussions: Union[int, str]):
        try:
            return int(telegram_ef_discussions)
        except:
            return telegram_ef_discussions

    # - Discord

    discord_token: str
    guild_name: str

    # - Notion

    notion_token: str

    # - Telegram and discord

    telegram_username_to_discord_aliases_json: str = "{}"

    # - OpenAI

    openai_api_key: str

    # - App

    filter_public_channels: bool = True
