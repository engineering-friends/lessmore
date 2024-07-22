import asyncio
import json

from lessmore.utils.file_primitives.local_path.local_path import local_path
from lessmore.utils.file_primitives.write_file import write_file


def sample_database_page_prepare():
    async def main():
        from learn_language_magic.deps import Deps
        from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient

        client = EnrichedNotionAsyncClient(
            auth=Deps.load().config.notion_token,
        )

        write_file(
            data=await client.pages.retrieve(page_id="54873a3a8061491e99b7fbe55e0dcc7b"),
            filename=local_path("sample_database_page.json"),
            writer=lambda data, file: json.dump(data, file, indent=2),
        )

    asyncio.run(main())


if __name__ == "__main__":
    sample_database_page_prepare()
