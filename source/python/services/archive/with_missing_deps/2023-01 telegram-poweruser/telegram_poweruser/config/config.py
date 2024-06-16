import os

from typing import Literal, Optional

from pydantic import BaseSettings


class Config(BaseSettings):
    # - Telegram

    telegram_phone: str
    telegram_api_id: str
    telegram_api_hash: str

    telegram_bot_name: str
    telegram_bot_token: str

    # - Notion

    notion_token: str

    # - Other

    central_channel_name: Optional[str]
    runtime_mode: Literal["test", "prod"]


# - Inflate config to environment variables

config = Config()  # note for dima: set default config values in the class definition

if __name__ == "__main__":
    print(config.telegram_bot_name)
    print(config.telegram_api_id)
    print(config.runtime_mode)
