import asyncio
import uuid

from lessmore.utils.printy import printy as print


def test_upsert_database():
    async def main():
        # - Init client

        from learn_language_magic.deps import Deps

        deps = Deps.load()

        from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient

        client = EnrichedNotionAsyncClient(
            auth=deps.config.notion_token,
        )

        # - Create page for tests inside tmp_page

        database_name = f"test_page_{uuid.uuid4()}"

        database = await client.upsert_database(
            database={
                "parent": {"page_id": deps.config.notion_test_page_id},
                "title": [{"text": {"content": database_name}}],
                "properties": {"word": {"id": "title", "name": "word", "title": {}, "type": "title"}},
            }
        )

        database = await client.upsert_database(
            database={
                "id": database["id"],
            },
            pages=[{"properties": {"word": {"title": [{"text": {"content": "Sure?!"}}]}}}],
            children_list=[[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}]],
        )

        # - Remove test database

        await client.upsert_database(database=database, archive=True)

    asyncio.run(main())


if __name__ == "__main__":
    test_upsert_database()
