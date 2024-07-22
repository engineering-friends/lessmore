import asyncio
import json

from lessmore.utils.asynchronous.async_cached_property import async_cached_property
from pydantic import BaseModel


class NotionDatabaseRow(BaseModel):
    def __init__(self, property_types: dict, **kwargs):
        self.property_types = property_types
        super().__init__(**kwargs)

    def get_column_names(self):
        result = []

        # add fields
        result += list(self.__fields__.keys())

        # add notion_properties

    @async_cached_property
    async def notion_page(self):
        # - Collect all dataclass fields and notion_properties

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
