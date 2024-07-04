import asyncio

from typing import Callable, Optional

from loguru import logger
from more_itertools import only
from notion_client import AsyncClient

from lessmore.utils.enriched_notion_client.test_paginated_request import test_paginated_request
from lessmore.utils.enriched_notion_client.test_upsert_database import test_upsert_database
from lessmore.utils.enriched_notion_client.test_upsert_page import test_upsert_page
from lessmore.utils.functional.contains_nested import contains_nested
from lessmore.utils.functional.dict.drop import drop
from lessmore.utils.tested import tested


class EnrichedNotionAsyncClient(AsyncClient):
    @staticmethod
    @tested(tests=[test_paginated_request])
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

    @tested(tests=[test_upsert_page])
    async def upsert_page(
        self,
        page: Optional[dict] = None,
        old_page: Optional[dict] = None,
        children: Optional[list] = None,
    ):
        # - Prepare kwargs

        # Note: it's very important to filter None values, or Notion will throw an ambiguous error
        page = {k: v for k, v in page.items() if v is not None}

        # - If not page_id: create page

        if "id" not in page:
            # - Create page

            logger.debug("Creating page", page=page)

            assert page.get("parent") is not None, "Parent is required to create a new page"

            page = await self.pages.create(**drop(page, ["id"]))

            # - Update children

            if children is not None:
                await self.blocks.children.append(block_id=page["id"], children=children)

            # - Return page

            return page

        assert "id" in page

        # - Update children if needed

        if children is not None:
            logger.debug("Get children", page=page)

            # - Get old children

            old_children = await self.get_paginated_request(method=self.blocks.children.list, block_id=page["id"])

            # - Update children if needed

            if not contains_nested(whole=old_children, part=children):
                logger.debug("Updating children", page=page)

                # - Delete old children

                for child in old_children:
                    try:
                        await self.blocks.delete(block_id=child["id"])
                    except Exception as e:
                        logger.error("Failed to delete child", child=child, error=e)

                # - Create new children

                await self.blocks.children.append(block_id=page["id"], children=children)

        # - Return if no update needed for properties and stuff

        if not drop(page, ["id"]):
            return old_page

        # - Update page

        # -- If old page provided - check if nothing has changed (to avoid unnecessary requests)

        if old_page and contains_nested(whole=old_page, part=page):
            return old_page

        # -- Update page

        logger.debug("Updating page", page=page)

        return await self.pages.update(page_id=page["id"], **drop(page, ["id"]))

    @tested(tests=[test_upsert_database])
    async def upsert_database(
        self,
        database: Optional[dict] = None,
        pages: list[dict] = [],
        remove_others: bool = False,
        page_unique_id_func: Optional[Callable] = None,
        archive: Optional[bool] = None,
    ):
        # - If archived - just archive

        if archive is not None:
            assert "id" in database, "Database id is required to archive it"
            return await self.blocks.update(block_id=database["id"], archived=True)

        # - Prepare kwargs

        database = {k: v for k, v in database.items() if v is not None}

        # - Create database if not exists

        if "id" not in database:
            logger.debug("Creating new database", database=database)

            database = await self.databases.create(**database)
            database_id = database["id"]

            if pages:
                await asyncio.gather(
                    *[self.upsert_page(page={**{"database_id": database_id}, **page}) for page in pages]
                )

            return database

        assert "id" in database

        # - Update metadata first

        if drop(database, ["id"]):
            # - Update database

            logger.info("Updating database", database_id=database, database=database)

            database = await self.databases.update(database_id=database["id"], **drop(database, ["id"]))
        else:
            # - Just retrieve database

            database = await self.databases.retrieve(database_id=database["id"])

        # - Update pages

        # -- Return if no pages provided

        if not pages:
            return database

        # - -- Get old pages

        old_pages = await self.get_paginated_request(method=self.databases.query, database_id=database["id"])

        # -- Find correct page_id for each page

        if page_unique_id_func:
            # - Set _unique_id

            for page in old_pages + pages:
                page["_unique_id"] = page_unique_id_func(page)

            # - Set page id for matching _unique_id

            for page in pages:
                old_page = only(
                    [old_page for old_page in old_pages if old_page["_unique_id"] == page["_unique_id"]], default=None
                )
                if old_page:
                    page["id"] = old_page["id"]

            # - Remove _unique_id

            for page in old_pages + pages:
                del page["_unique_id"]

        # -- Remove pages if needed

        if remove_others:
            to_remove = [page for page in old_pages if page["id"] not in [page.get("id") for page in pages]]

            logger.debug("Removing pages", n_pages=len(to_remove))

            await asyncio.gather(*[self.upsert_page(page={"id": page["id"], "archived": True}) for page in to_remove])

        # -- Create or update new pages

        logger.debug(
            "Upserting pages",
            pages=[
                {
                    "database_id": database["id"],
                    **page,
                }
                for page in pages
            ],
        )

        await asyncio.gather(
            *[
                self.upsert_page(
                    page={
                        "parent": {"database_id": database["id"]},
                        **drop(page, ["children"]),
                    },
                    old_page=only(
                        [old_page for old_page in old_pages if old_page["id"] == page.get("id")],
                        default=None,
                    ),
                    children=page.get("children"),
                )
                for page in pages
            ]
        )

        return database
