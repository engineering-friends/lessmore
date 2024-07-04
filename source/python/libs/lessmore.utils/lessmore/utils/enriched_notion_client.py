import asyncio
import time
import uuid

from typing import Callable, Optional

from lessmore.utils.functional.contains_nested import contains_nested
from lessmore.utils.printy import printy as print
from loguru import logger
from more_itertools import first, only
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

    async def upsert_page(
        self,
        page_id: Optional[str] = None,
        parent: Optional[dict] = None,
        old_page: Optional[dict] = None,
        archived: Optional[bool] = None,
        properties: Optional[dict] = None,
        icon: Optional[dict] = None,
        cover: Optional[dict] = None,
        children: Optional[list] = None,
    ):
        # - Prepare kwargs

        kwargs = {"archived": archived, "properties": properties, "icon": icon, "cover": cover, "parent": parent}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # - If not page_id: create page

        if not page_id:
            # - Create page

            page = await self.pages.create(**kwargs)

            assert parent is not None, "Parent is required to create a new page"

            # - Update children

            if children is not None:
                await self.blocks.children.append(block_id=page["id"], children=children)

            # - Return page

            return page

        # - Update children if needed

        if children is not None:
            # - Get old children

            old_children = await self.get_paginated_request(method=self.blocks.children.list, block_id=page_id)

            # - Update children if needed

            if not contains_nested(whole=old_children, part=children):
                logger.trace("Updating children", page_id=page_id)

                # - Delete old children

                await asyncio.gather(*[self.blocks.delete(block_id=child["id"]) for child in old_children])

                # - Create new children

                await self.blocks.children.append(block_id=page_id, children=children)

        # - Update page

        # -- Return if no kwargs provided

        if not kwargs:
            return old_page

        # -- If old page provided - check if nothing has changed (to avoid unnecessary requests)

        if old_page and contains_nested(whole=old_page, part=kwargs):
            return old_page

        # -- Update page

        logger.trace("Updating page", page_id=page_id)

        return await self.pages.update(page_id=page_id, **kwargs)

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
            database = await self.databases.create(**kwargs)
            database_id = database["id"]

            if pages:
                await asyncio.gather(*[self.upsert_page(parent={"database_id": database_id}, **page) for page in pages])

            return database

        # - Update metadata first

        if kwargs:
            # - Update database

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

        # -- Remove pages if needed

        if remove_others:
            to_remove = [page for page in old_pages if page["id"] not in [page["id"] for page in pages]]
            await asyncio.gather(*[self.upsert_page(page_id=page["id"], archived=True) for page in to_remove])

        # -- Create or update new pages

        await asyncio.gather(*[self.upsert_page(parent={"database_id": database_id}, **page) for page in pages])

        return database


def test_paginated_request():
    async def main():
        from learn_language_magic.deps import Deps

        client = EnrichedNotionAsyncClient(
            auth=Deps.load().config.notion_token,
        )

        print(await client.pages.retrieve(page_id="20901ecb09f8406983ff47f18d24f2a6"))

    asyncio.run(main())


def test_upsert_page():
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
            parent={"page_id": deps.config.notion_test_page_id},
            properties={"title": {"title": [{"text": {"content": page_name}}]}},
        )

        new_page = await client.upsert_page(
            page_id=page["id"],
            old_page=page,
            children=[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}],
        )

        new_page = await client.upsert_page(  # should not update anything if nothing has changed
            page_id=page["id"],
            old_page=page,
            children=[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}],
        )

        assert contains_nested(
            whole=new_page, part={"properties": {"title": {"title": [{"text": {"content": page_name}}]}}}
        )

        # - Remove test page

        await client.upsert_page(page_id=page["id"], archived=True)

    asyncio.run(main())


def test_upsert_database():
    async def main():
        # - Init client

        from learn_language_magic.deps import Deps

        deps = Deps.load()

        client = EnrichedNotionAsyncClient(
            auth=deps.config.notion_token,
        )
        print(await client.databases.retrieve(database_id="d7a47aa34d2448e38e1a62ed7b6c6775"))

        # - Create page for tests inside tmp_page

        database_name = f"test_page_{uuid.uuid4()}"

        database = await client.upsert_database(
            parent={"page_id": deps.config.notion_test_page_id},
            title=[{"text": {"content": database_name}}],
            properties={"word": {"id": "title", "name": "word", "title": {}, "type": "title"}},
        )

        database = await client.upsert_database(
            database_id=database["id"],
            pages=[
                {
                    "children": [{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}],
                    "properties": {"word": {"title": [{"text": {"content": "Sure?!"}}]}},
                }
            ],
        )

        # - Remove test database

        await client.upsert_database(database_id=database["id"], archived=True)

    asyncio.run(main())


if __name__ == "__main__":
    # test_paginated_request()
    # test_upsert_page()
    test_upsert_database()
