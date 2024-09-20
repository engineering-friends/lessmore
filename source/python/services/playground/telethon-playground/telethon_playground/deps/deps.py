import os

from dataclasses import dataclass
from pathlib import Path

import openai

from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient
from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config
from telethon import TelegramClient
from telethon_playground.deps.config.config import Config


@dataclass
class Deps:
    config: Config
    local_files_dir: Path
    telegram_bot_client: TelegramClient
    telegram_user_client: TelegramClient

    @staticmethod
    def load(log_level="DEBUG", env: str = "test") -> "Deps":
        # - Setup loguru

        setup_json_loguru(level=log_level)

        # - Init config

        config = Config(**read_config([f"{str(Path(__file__).parent)}/config/config.{env}.yaml"]))

        local_files_dir = Path(__file__).parent / f"../data/dynamic/{env}"

        # - Build deps

        return Deps(
            config=config,
            local_files_dir=local_files_dir,
            telegram_bot_client=TelegramClient(
                session=ensure_path(str(local_files_dir / "telegram_bot.session")),
                api_id=int(config.telegram_api_id),
                api_hash=config.telegram_api_hash,
            ),
            telegram_user_client=TelegramClient(
                session=ensure_path(local_files_dir / "telegram_user.session"),
                api_id=int(config.telegram_api_id),
                api_hash=config.telegram_api_hash,
            ),
        )

    def notion_client(self) -> EnrichedNotionAsyncClient:
        return EnrichedNotionAsyncClient(auth=self.config.notion_token)


def test():
    print(Deps.load().config)


if __name__ == "__main__":
    test()
