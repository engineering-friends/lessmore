import asyncio

from notion_client import AsyncClient


class EnrichedNotionAsyncClient(AsyncClient):
    @staticmethod
    async def get_paginated_request(method, **kwargs):
        # - Init

        result = []
        start_cursor = None
        has_more = True

        # - Get data from notion

        while has_more:
            response = await method(start_cursor=start_cursor, **kwargs)
            result.extend(response["results"])
            start_cursor = response["next_cursor"]
            has_more = response["has_more"]

        return result


def test():
    async def main():
        from learn_language_magic.deps import Deps

        client = EnrichedNotionAsyncClient(
            auth=Deps.load().config.notion_token,
        )
        from lessmore.utils.printy import printy

        printy(
            await client.get_paginated_request(
                method=client.databases.query,
                database_id="a4f6eaf88dbc4402a8232ab56484ee03",
            ),
        )

    asyncio.run(main())


if __name__ == "__main__":
    test()
