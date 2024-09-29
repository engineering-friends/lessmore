from pathlib import Path

from ef_bots.ef_threads.deps.config.config import Config
from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient
from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.loguru_utils.setup_json_loguru import setup_json_loguru
from lessmore.utils.read_config.read_config import read_config
from telethon import TelegramClient


class Deps:
    config: Config
    local_files_dir: Path | str
    telegram_user_client: TelegramClient
    notion_client: EnrichedNotionAsyncClient

    def __init__(self, log_level="DEBUG", env: str = "test"):
        # - Setup loguru

        setup_json_loguru(level=log_level)

        # - Init config

        config = Config(**read_config([f"{str(Path(__file__).parent)}/config/config.{env}.yaml"]))

        local_files_dir = Path(__file__).parent / f"data/dynamic/{env}"

        self.config = config
        self.local_files_dir = str(local_files_dir)
        self.telegram_user_client = TelegramClient(
            session=ensure_path(local_files_dir / "telegram_user.session"),
            api_id=int(config.telegram_api_id),
            api_hash=config.telegram_api_hash,
        )
        self.notion_client = EnrichedNotionAsyncClient(auth=self.config.notion_token)

    async def __aenter__(self):
        await self.telegram_user_client.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def test():
    print(Deps().config)


if __name__ == "__main__":
    test()
