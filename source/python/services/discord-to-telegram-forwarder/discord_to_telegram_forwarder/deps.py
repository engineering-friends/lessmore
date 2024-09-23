import os

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import openai

from discord_to_telegram_forwarder.config.config import Config
from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config
from telethon import TelegramClient


@dataclass
class Deps:
    config: Config
    cache: dict
    local_files_dir: str
    telegram_bot_client: TelegramClient
    telegram_user_client: TelegramClient

    @staticmethod
    def load(
        env: Literal["test", "prod"] = "test",
        log_level="DEBUG",
        config_dict: dict = {},
    ) -> "Deps":
        # - Init config

        config = Config(
            **read_config(
                [
                    str(Path(__file__).parent / f"config/config.{env}.yaml"),
                    config_dict,
                ]
            )
        )

        # - Configure openai

        openai.api_key = config.openai_api_key

        # - Init logger

        setup_json_loguru(
            append_non_json_traceback=(env.lower() == "test"),
            level=log_level,
        )

        # - Get data path

        local_files_dir = ensure_path(Path(__file__).parent / f"../data/dynamic/{env}", is_dir=True)

        return Deps(
            config=config,
            cache={},
            local_files_dir=local_files_dir,
            telegram_bot_client=TelegramClient(
                session=str(local_files_dir / "telegram_bot.session"),
                api_id=int(config.telegram_api_id),
                api_hash=config.telegram_api_hash,
            ),
            telegram_user_client=TelegramClient(
                session=str(local_files_dir / "telegram_user.session"),
                api_id=int(config.telegram_api_id),
                api_hash=config.telegram_api_hash,
            ),
        )


def test():
    print(type(Deps.load().config.telegram_ef_channel))


if __name__ == "__main__":
    test()
