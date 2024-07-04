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
            page={
                "parent": {"page_id": deps.config.notion_test_page_id},
                "properties": {"title": {"title": [{"text": {"content": page_name}}]}},
            },
            children=[
                {
                    "type": "image",
                    "image": {
                        "type": "external",
                        "external": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Random_Radio_Bruno_Festival_di_Sanremo_2021.png/440px-Random_Radio_Bruno_Festival_di_Sanremo_2021.png",
                        },
                    },
                }
            ],
        )

        # new_page = await client.upsert_page(
        #     page={"id": page["id"]},
        #     old_page=page,
        #     children=[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}],
        # )
        #
        # new_page = await client.upsert_page(  # should not change anything
        #     page={"id": page["id"]},
        #     old_page=page,
        #     children=[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}],
        # )
        #
        # assert contains_nested(
        #     whole=new_page, part={"properties": {"title": {"title": [{"text": {"content": page_name}}]}}}
        # )

        # - Remove test page

        # await client.upsert_page(page={"id": page["id"], "archived": True})

    asyncio.run(main())


if __name__ == "__main__":
    test_upsert_page()
