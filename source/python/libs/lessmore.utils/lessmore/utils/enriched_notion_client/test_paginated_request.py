import asyncio

from lessmore.utils.printy import printy as print


def test_paginated_request():
    from lessmore.utils.enriched_notion_client.enriched_notion_client import EnrichedNotionAsyncClient

    async def main():
        from learn_language_magic.deps import Deps

        client = EnrichedNotionAsyncClient(
            auth=Deps.load().config.notion_token,
        )

        print(
            await client.get_paginated_request(
                method=client.pages.retrieve, method_kwargs={"page_id": "20901ecb09f8406983ff47f18d24f2a6"}
            )
        )
        print(await client.pages.retrieve(page_id="20901ecb09f8406983ff47f18d24f2a6"))

    asyncio.run(main())


if __name__ == "__main__":
    test_paginated_request()
