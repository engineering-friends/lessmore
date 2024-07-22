import asyncio
import uuid

from dataclasses import dataclass
from typing import Optional

from inline_snapshot import snapshot
from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from lessmore.utils.asynchronous.async_cached_property import prefetch_all_cached_properties
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests
from loguru import logger

from notion_database_ai.build_notion_page import build_notion_page
from notion_database_ai.column.auto_column import auto_column
from notion_database_ai.column.column import column
from notion_database_ai.column.extract_column_infos import extract_column_infos


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

    logger.info("Got pages", n_pages=len(pages))

    if not pages:
        return

    # - Get property types

    property_types = {
        k: v["type"] for k, v in (await client.databases.retrieve(database_id=database_id))["properties"].items()
    }

    # - Extract columns

    column_infos = extract_column_infos(row_class)

    # - Assert all column names are present in notion page

    for column_info in column_infos:
        assert column_info.name in property_types, f"Property {column_info.name} is not present"

    # - Build rows

    rows = [
        row_class(
            **{
                column_info.attribute: client.plainify_database_property(page["properties"][column_info.name])
                for column_info in column_infos
                if not column_info.is_auto
            },
        )
        for page in pages
    ]

    # - Calculate rows

    logger.info("Prefetching all auto columns")

    await asyncio.gather(*[prefetch_all_cached_properties(row) for row in rows])

    # - Get notion pages

    logger.info("Building notion pages")

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

    logger.info("Updating notion pages")

    await client.upsert_database(
        database={"id": database_id},
        pages=new_pages,
        remove_others=False,
    )


def test():
    async def main(database: Optional[dict] = None):
        # - Init client

        from learn_language_magic.deps import Deps

        deps = Deps.load()

        from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient

        client = EnrichedNotionAsyncClient(
            auth=deps.config.notion_token,
        )

        # - Create page for tests inside tmp_page

        if not database:
            database_name = f"test_page_{uuid.uuid4()}"

            database = await client.upsert_database(
                database={
                    "parent": {"page_id": deps.config.notion_test_page_id},
                    "title": [{"text": {"content": database_name}}],
                    "properties": {
                        "title": {
                            "id": "title",
                            "name": "word",
                            "title": {},
                            "type": "title",
                        },
                        "Number": {
                            "id": "number",
                            "name": "number",
                            "number": {},
                            "type": "number",
                        },
                        "name": {"id": "name", "name": "name", "rich_text": {}, "type": "rich_text"},
                        "Foo": {"id": "foo", "name": "foo", "rich_text": {}, "type": "rich_text"},
                    },
                }
            )

            database = await client.upsert_database(
                database={
                    "id": database["id"],
                },
                pages=[
                    {
                        "properties": {
                            "title": {"title": [{"text": {"content": "Test Title"}}]},
                            "Number": {"number": 1},
                        }
                    }
                ],
                children_list=[[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}]],
            )

        @dataclass
        class Example:
            title: str
            number: int = column(alias="Number")

            @auto_column
            async def name(self):
                return "Example"

            @auto_column(alias="Foo")
            async def foo(self):
                return "Foo"

        await update_notion_database(
            database_id=database["id"],
            row_class=Example,
            notion_token=deps.config.notion_token,
        )

    asyncio.run(main(database={"id": "6834e1ab38ec42c9b9c505ef07a4361a"}))  # pragma: allowlist secret


if __name__ == "__main__":
    test()
