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
        page["properties"] = {k: v for k, v in page.get("properties", {}).items() if v is not None}
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

        # - Return if page was just for creation

        if not page:
            return old_page

        # - Update children if needed

        if children is not None:
            # - Get old children

            old_children = await self.get_paginated_request(method=self.blocks.children.list, block_id=page["id"])

            # - Update children if needed

            if not contains_nested(whole=old_children, part=children):
                logger.debug("Updating children", page=page)

                # - Delete old children

                for child in old_children:
                    await self.blocks.delete(block_id=child["id"])
                # await asyncio.gather(*[self.blocks.delete(block_id=child["id"]) for child in old_children])

                # - Create new children

                await self.blocks.children.append(block_id=page["id"], children=children)

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
        database_id: Optional[str] = None,
        parent: Optional[dict] = None,
        properties: Optional[dict] = None,
        title: Optional[list] = None,
        description: Optional[str] = None,
        icon: Optional[dict] = None,
        cover: Optional[dict] = None,
        is_inline: Optional[bool] = None,
        pages: list[dict] = [],
        remove_others: bool = False,
        page_unique_id_func: Optional[Callable] = None,
        archived: Optional[bool] = None,
        update_page_contents: bool = True,
    ):
        # - If archived - just archive

        if archived is not None:
            return await self.blocks.update(block_id=database_id, archived=True)

        # - Prepare kwargs

        kwargs = {
            "properties": properties,
            "title": title,
            "description": description,
            "icon": icon,
            "cover": cover,
            "is_inline": is_inline,
            "parent": parent,
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # - Create database if not exists

        if not database_id:
            logger.debug("Creating new database", kwargs=kwargs)

            database = await self.databases.create(**kwargs)
            database_id = database["id"]

            if pages:
                await asyncio.gather(
                    *[self.upsert_page(page={**{"database_id": database_id}, **page}) for page in pages]
                )

            return database

        # - Update metadata first

        if kwargs:
            # - Update database

            logger.info("Updating database", database_id=database_id, kwargs=kwargs)

            database = await self.databases.update(database_id=database_id, **kwargs)
        else:
            # - Just retrieve database

            database = await self.databases.retrieve(database_id=database_id)

        # - Update pages

        # -- Return if no pages provided

        if not pages:
            return database

        # - -- Get old pages

        old_pages = await self.get_paginated_request(method=self.databases.query, database_id=database_id)

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
            to_remove = [page for page in old_pages if page["id"] not in [page["id"] for page in pages]]

            logger.debug("Removing pages", n_pages=len(to_remove))

            await asyncio.gather(*[self.upsert_page(page={"id": page["id"], "archived": True}) for page in to_remove])

        # -- Create or update new pages

        await asyncio.gather(
            *[
                self.upsert_page(
                    parent={"database_id": database_id},
                    page=drop(page, ["children"] if not update_page_contents else []),
                )
                for page in pages
            ]
        )

        return database
