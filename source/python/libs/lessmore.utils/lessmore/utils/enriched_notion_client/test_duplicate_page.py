import asyncio
import uuid

from lessmore.utils.functional.contains_nested import contains_nested


def test_duplicate_page():
    from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient

    async def main():
        # - Init client

        from learn_language_magic.deps import Deps

        deps = Deps.load()

        client = EnrichedNotionAsyncClient(
            auth=deps.config.notion_token,
        )

        # - Create page for tests inside tmp_page

        await client.duplicate_page(
            page_id="106b738eed9a807693efe724b1f1852c",  # https://www.notion.so/8c93fa8355344cbd88544b3a076ef552
            target_page_id="106b738eed9a80389551e5ae2b8b4efc",  # https://www.notion.so/5caeefe3bf5645b39b0995f02fc55b82
        )

    asyncio.run(main())


if __name__ == "__main__":
    test_duplicate_page()
