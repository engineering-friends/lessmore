import asyncio

from typing import Optional

from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from lessmore.utils.asynchronous.async_cached_property import prefetch_all_cached_properties
from notion_database_ai.build_notion_page import build_notion_page
from notion_database_ai.get_properties_to_attribute_name import get_property_name_to_attribute_name


SUPPORTED_PROPERTIES = ["title", "text", "number", "select", "multi-select", "date"]


async def update_notion_database(
    database_id: str,
    row_class: type,
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
            **{
                k: client.plainify_database_property(v)
                for k, v in page["properties"].items()
                if v["type"] in SUPPORTED_PROPERTIES
            },
        )
        for page in pages
    ]

    # - Get property_name_to_attribute_name

    property_name_to_attribute_name = get_property_name_to_attribute_name(rows[0])

    # - Assert all properties are in place

    assert set(property_name_to_attribute_name.keys()).issubset(
        set(property_types.keys())
    ), f"Notion page: {list(property_types.keys())}, your dataclass: {list(property_name_to_attribute_name.keys())}"

    # - Calculate rows

    await asyncio.gather(*[prefetch_all_cached_properties(row) for row in rows])

    # - Get notion pages

    new_pages = await asyncio.gather(
        *[
            build_notion_page(
                row=row,
                property_types=property_types,
            )
            for i, row in enumerate(rows)
        ]
    )

    # - Add ids of original pages

    for i, row in enumerate(pages):
        new_pages[i]["id"] = row["id"]

    # - Update notion pages

    await client.upsert_database(
        database={"id": database_id},
        pages=new_pages,
        remove_others=False,
    )
