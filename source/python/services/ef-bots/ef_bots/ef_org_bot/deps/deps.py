from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from ef_bots.ef_org_bot.deps.config.config import Config
from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient
from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config
from loguru import logger
from teletalk.app import App
from telethon import TelegramClient


class Deps:
    def __init__(self, env: str = "test", log_level="DEBUG"):
        # - Setup loguru

        setup_json_loguru(level=log_level)

        # - Init config

        config = Config(**read_config([f"{str(Path(__file__).parent)}/config/config.{env}.yaml"]))

        local_files_dir = Path(__file__).parent / f"../data/dynamic/{env}"

        # - Build deps

        self.config = config
        self.local_files_dir = local_files_dir

        # no need to this one yet
        # self.telegram_bot_client = TelegramClient(
        #     session=ensure_path(str(local_files_dir / "telegram_bot.session")),
        #     api_id=int(config.telegram_api_id),
        #     api_hash=config.telegram_api_hash,
        # )
        self.telegram_user_client = TelegramClient(
            session=ensure_path(local_files_dir / "telegram_user.session"),
            api_id=int(config.telegram_api_id),
            api_hash=config.telegram_api_hash,
        )

    def notion_client(self) -> EnrichedNotionAsyncClient:
        return EnrichedNotionAsyncClient(auth=self.config.notion_token)

    @asynccontextmanager
    async def stack(self):
        await self.telegram_user_client.start()

        yield (
            self,
            await App(
                bot=self.config.telegram_bot_token,
                state_backend="rocksdict",
                state_config={"path": str(self.local_files_dir / "app_state")},
            ).__aenter__(),
        )


def test():
    print(Deps(env="test").config)


if __name__ == "__main__":
    test()
