import asyncio
import time
import uuid

from typing import Optional

from lessmore.utils.functional.contains_nested import contains_nested
from lessmore.utils.printy import printy as print
from loguru import logger
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

    async def update_page(
        self,
        page_id: str,
        archived: Optional[bool] = None,
        properties: Optional[dict] = None,
        icon: Optional[str] = None,  # todo later: check that this type [@marklidenberg]
        cover: Optional[dict] = None,  # todo later: check that this type [@marklidenberg]
        old_page: Optional[dict] = None,
        children: Optional[list] = None,
    ):
        # - Prepare kwargs

        kwargs = {"archived": archived, "properties": properties, "icon": icon, "cover": cover}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

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

        # - If old page provided - check if nothing has changed (to avoid unnecessary requests)

        if old_page and contains_nested(whole=old_page, part=kwargs):
            return old_page

        # - Update page

        logger.trace("Updating page", page_id=page_id)

        return await self.pages.update(page_id=page_id, **kwargs)


def test_paginated_request():
    async def main():
        from learn_language_magic.deps import Deps

        client = EnrichedNotionAsyncClient(
            auth=Deps.load().config.notion_token,
        )

        print(await client.pages.retrieve(page_id="20901ecb09f8406983ff47f18d24f2a6"))

    asyncio.run(main())


def test_update_page():
    async def main():
        # - Init client

        from learn_language_magic.deps import Deps

        deps = Deps.load()

        client = EnrichedNotionAsyncClient(
            auth=deps.config.notion_token,
        )

        # - Create page for tests inside tmp_page

        page_name = f"test_page_{uuid.uuid4()}"
        page = await client.pages.create(
            parent={"page_id": deps.config.notion_test_page_id},
            properties={"title": {"title": [{"text": {"content": page_name}}]}},
        )

        new_page = await client.update_page(
            page_id=page["id"],
            old_page=page,
            children=[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}],
        )

        new_page = await client.update_page(  # should not update anything if nothing has changed
            page_id=page["id"],
            old_page=page,
            children=[{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Hello!"}}]}}],
        )

        assert contains_nested(
            whole=new_page, part={"properties": {"title": {"title": [{"text": {"content": page_name}}]}}}
        )

        # - Remove test page

        await client.pages.update(page_id=page["id"], archived=True)

    asyncio.run(main())


if __name__ == "__main__":
    # test_paginated_request()
    test_update_page()
