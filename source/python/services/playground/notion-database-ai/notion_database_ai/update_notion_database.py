import asyncio

from typing import Optional

from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from lessmore.utils.asynchronous.async_cached_property import prefetch_all_cached_properties
from notion_database_ai.database_row.notion_database_row import NotionDatabaseRow


SUPPORTED_PROPERTIES = ["title", "text", "number", "select", "multi-select", "date"]


async def update_notion_database(
    database_id: str,
    row_class: type[NotionDatabaseRow],
    notion_token: Optional[str] = None,
):
    # - Init notion client

    client = NotionRateLimitedClient(auth=notion_token)

    # - Get current notion pages

    pages = await client.get_paginated_request(
        method=client.databases.query,
        method_kwargs=dict(database_id=database_id),
    )

    if not pages:
        return

    # - Get row types from the first page

    property_types = {k: v["type"] for k, v in pages[0]["properties"].items()}

    # - Build rows

    rows = [
        row_class(
            property_types=property_types,
            **{
                k: client.plainify_database_property(v)
                for k, v in page["properties"].items()
                if v["type"] in SUPPORTED_PROPERTIES
            },
        )
        for page in pages
    ]

    # - Update rows

    await asyncio.gather(*([prefetch_all_cached_properties(row) for row in rows]))

    # - Update notion pages

    await client.upsert_database(
        database={"id": database_id},
        pages=await asyncio.gather(*[row.notion_page for row in rows]),
        page_unique_id_func=lambda page: page["properties"]["name"]["title"][0]["text"]["content"],
        remove_others=False,
    )
