import asyncio
import uuid

from lessmore.utils.functional.contains_nested import contains_nested


def test_upsert_page():
    from lessmore.utils.enriched_notion_client.enriched_notion_client import EnrichedNotionAsyncClient

    async def main():
        # - Init client

        from learn_language_magic.deps import Deps

        deps = Deps.load()

        client = EnrichedNotionAsyncClient(
            auth=deps.config.notion_token,
        )

        # - Create page for tests inside tmp_page

        page_name = f"test_page_{uuid.uuid4()}"

        page = await client.upsert_page(
            parent={"page_id": deps.config.notion_test_page_id},
            properties={"title": {"title": [{"text": {"content": page_name}}]}},
        )

        new_page = await client.upsert_page(
            page_id=page["id"],
            old_page=page,
            children=[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}],
        )

        new_page = await client.upsert_page(  # should not update anything if nothing has changed
            page_id=page["id"],
            old_page=page,
            children=[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}],
        )

        assert contains_nested(
            whole=new_page, part={"properties": {"title": {"title": [{"text": {"content": page_name}}]}}}
        )

        # - Remove test page

        await client.upsert_page(page_id=page["id"], archived=True)

    asyncio.run(main())


if __name__ == "__main__":
    test_upsert_page()
