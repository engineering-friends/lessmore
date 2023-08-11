import os

from pydantic import BaseSettings

from lessmore.utils.load_pydantic_settings.load_pydantic_settings import load_pydantic_settings


class Config(BaseSettings):
    # - Telegram

    telegram_api_id: str
    telegram_api_hash: str
    telegram_bot_name: str
    telegram_bot_token: str


# - Inflate config to environment variables

config = load_pydantic_settings(
    pydantic_class=Config,
    config_source=[
        {
            "type": "file",
            "is_required": False,
            "value": "{root}/common.yaml",
        },
        {
            "type": "file",
            "is_required": False,
            "value": "{root}/common.secrets.yaml",
        },
        {
            "type": "file",
            "is_required": False,
            "value": "{root}/common.local.yaml",
        },
        {
            "type": "file",
            "is_required": True,
            "value": "{root}/environments/{environment}.yaml",
        },
        {
            "type": "file",
            "is_required": False,
            "value": "{root}/environments/{environment}.local.yaml",
        },
        "environment_variables",
    ],
    context={
        "root": os.path.dirname(__file__),
        "environment": os.environ.get("telegram_poweruser_environment", "prod"),
    },
)

if __name__ == "__main__":
    print(config.telegram_bot_name)
    print(config.telegram_api_id)
    print(config.runtime_mode)
