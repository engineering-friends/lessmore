import asyncio

from lessmore.utils.printy import printy as print


def test_paginated_request():
    async def main():
        from learn_language_magic.deps import Deps

        from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient

        client = EnrichedNotionAsyncClient(
            auth=Deps.load().config.notion_token,
        )
        # print(
        #     await client.get_paginated_request(
        #         method=client.databases.query,
        #         method_kwargs={
        #             "database_id": "60682eb4e436490782307b4073a02731",
        #         },
        #     )
        # )
        print(await client.pages.retrieve(page_id="54873a3a8061491e99b7fbe55e0dcc7b"))

    asyncio.run(main())


if __name__ == "__main__":
    test_paginated_request()
