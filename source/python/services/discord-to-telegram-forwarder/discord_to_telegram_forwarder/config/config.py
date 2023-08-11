import os

from pydantic import BaseSettings

from lessmore.utils.load_pydantic_settings.load_pydantic_settings import load_pydantic_settings
from lessmore.utils.path_helpers.get_current_dir import get_current_dir


class Config(BaseSettings):
    # - Telegram

    telegram_api_id: str
    telegram_api_hash: str
    telegram_bot_name: str
    telegram_bot_token: str
    channel_name: str

    # - Discord

    discord_token: str

    # - OpenAI

    openai_api_key: str


# - Inflate config to environment variables

config: Config = load_pydantic_settings(
    pydantic_class=Config,
    config_source=[
        {
            "type": "file",
            "is_required": False,
            "value": "{root}/config.secrets.yaml",
        },
        "environment_variables",
    ],
    context={
        "root": str(get_current_dir()),
    },
)

if __name__ == "__main__":
    print(config.telegram_bot_name)
    print(config.telegram_api_id)
