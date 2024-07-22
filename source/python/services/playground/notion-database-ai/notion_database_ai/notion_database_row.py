import asyncio
import json
import re
import textwrap

from dataclasses import dataclass

from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from learn_language_magic.markdown_table_to_df import markdown_table_to_df
from lessmore.utils.asynchronous.async_cached_property import async_cached_property, prefetch_all_cached_properties
from lessmore.utils.enriched_notion_client.enriched_notion_client import EnrichedNotionAsyncClient
from more_itertools import mark_ends


@dataclass
class NotionDatabaseRow:
    @async_cached_property
    async def notion_page(self):
        # - Collect all dataclass fields and notion_properties
        # - Build properties

        result = {
            "properties": {
                "name": {"title": [{"text": {"content": self.name}}]},
                "applications": {"rich_text": [{"text": {"content": await self.applications}}]},
                # number
                "github_stars": {"number": int((await self.github_stars) or 0)},
                "short_description": {"rich_text": [{"text": {"content": await self.short_description}}]},
                "killer_features": {"rich_text": [{"text": {"content": await self.killer_features}}]},
                "why_people_hate_it": {
                    "rich_text": [{"text": {"content": await self.why_people_hate_it}}],
                },
                "managed_only": {"checkbox": await self.managed_only},
            },
            "children": None,
        }

        # - Filter out None values

        result = {k: v for k, v in result.items() if v is not None}

        # - Remove ** from all the answers

        result = json.loads(json.dumps(result, ensure_ascii=False).replace("**", ""))

        return result


def test():
    async def main():
        pass

    asyncio.run(main())


if __name__ == "__main__":
    test()
