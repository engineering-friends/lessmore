import os

from pathlib import Path
from typing import Literal

import loguru

from discord_to_telegram_forwarder.config import Config
from discord_to_telegram_forwarder.context.context import Context
from telethon import TelegramClient

from lessmore.utils.load_pydantic_settings.load_pydantic_settings import load_pydantic_settings


def init_default_context(env: Literal["test", "prod"] = "test"):
    # - Init config

    config = load_pydantic_settings(
        pydantic_class=Config,
        config_source=[
            {
                "type": "file",
                "is_required": False,
                "value": "{root}/config.secrets.{env}.yaml",
            },
            # "environment_variables",
        ],
        context={
            "root": str(Path(__file__).parent),
            "env": os.environ.get("DISCORD_TO_TELEGRAM_FORWARDER_ENV", env),
        },
    )

    # - Return context

    return Context(
        config=config,
        logger=loguru.Logger(),
        telegram_bot_client=TelegramClient(
            session=str(Path(__file__).parent / "telegram_user.session"),
            api_id=int(config.telegram_api_id),
            api_hash=config.telegram_api_hash,
        ),
        telegram_user_client=TelegramClient(
            session=str(Path(__file__).parent / "telegram_user.session"),
            api_id=int(config.telegram_api_id),
            api_hash=config.telegram_api_hash,
        ),
    )
