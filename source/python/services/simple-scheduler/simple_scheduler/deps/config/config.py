from typing import Union

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    telegram_bot_name: str
    telegram_bot_token: str
    notion_token: str
