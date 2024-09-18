from typing import Union

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # - Telegram

    telegram_test_chat_id: int
    telegram_api_id: str
    telegram_api_hash: str
    telegram_bot_name: str
    telegram_bot_token: str
    telegram_ef_channel: Union[int, str]
