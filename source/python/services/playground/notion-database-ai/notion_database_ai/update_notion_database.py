import asyncio

from typing import Optional

from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from lessmore.utils.asynchronous.async_cached_property import prefetch_all_cached_properties
from notion_database_ai.notion_database_row import NotionDatabaseRow


async def update_notion_database(
    database_id: str,
    row: type[NotionDatabaseRow],
    notion_token: Optional[str] = None,
    openai_token: Optional[str] = None,
):
    # - Init notion client

    client = NotionRateLimitedClient(auth=notion_token)

    # - Get current notion pages

    # - Build rows

    # - Update rows

    # - Prefetch all properties

    await asyncio.gather(*([prefetch_all_cached_properties(row) for row in []]))

    # - Update notion pages

    await client.upsert_database(
        database={"id": database_id},
        pages=await asyncio.gather(*[row.notion_page for row in []]),
        page_unique_id_func=lambda page: page["properties"]["name"]["title"][0]["text"]["content"],
        remove_others=False,
    )

    # - Update notion pages
