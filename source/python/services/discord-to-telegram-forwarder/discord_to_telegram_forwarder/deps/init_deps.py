import os
import sys

from pathlib import Path
from typing import Literal

import openai

from discord_to_telegram_forwarder.config.config import Config
from discord_to_telegram_forwarder.deps.deps import Deps
from loguru import logger
from telethon import TelegramClient

from lessmore.utils.configure_loguru.format_as_json_colored.format_as_json_colored import format_as_json_colored
from lessmore.utils.read_config.read_config import read_config


def init_deps(env: Literal["test", "prod"] = "test", log_level="DEBUG") -> Deps:
    # - Init config

    config = Config(**read_config(str(Path(__file__).parent / f"../config/config.secrets.{env}.yaml")))

    # - Configure openai

    openai.api_key = config.openai_api_key

    # - Init logger

    logger.remove()
    logger.add(sink=sys.stdout, level=log_level, format=format_as_json_colored)

    # - Get data path

    local_files_dir = str(Path(__file__).parent / f"../../data/dynamic/{env}")

    # - Return context

    os.makedirs(local_files_dir, exist_ok=True)

    return Deps(
        config=config,
        cache={},
        local_files_dir=local_files_dir,
        telegram_bot_client=TelegramClient(
            session=str(Path(local_files_dir) / "telegram_bot.session"),
            api_id=int(config.telegram_api_id),
            api_hash=config.telegram_api_hash,
        ),
        telegram_user_client=TelegramClient(
            session=str(Path(local_files_dir) / f"telegram_user.session"),
            api_id=int(config.telegram_api_id),
            api_hash=config.telegram_api_hash,
        ),
    )


def test():
    print(type(init_deps().config.telegram_ef_discussions))


if __name__ == "__main__":
    test()
