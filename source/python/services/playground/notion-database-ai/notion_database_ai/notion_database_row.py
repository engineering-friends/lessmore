import asyncio
import inspect
import json

from lessmore.utils.asynchronous.async_cached_property import async_cached_property
from notion_database_ai.notion_property import notion_property
from pydantic import BaseModel


class NotionDatabaseRow:
    def __init__(self, property_types: dict, **kwargs):
        self.property_types = property_types
        super().__init__(**kwargs)

        # - Get each property at least once to ensure that metadata is loaded for "notion_properties"

        for attr_name in dir(self):
            getattr(self, attr_name)

    def get_column_names(self):
        result = []

        # add fields
        # result += list(self.__fields__.keys())

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
        class Example(NotionDatabaseRow):
            @notion_property
            async def name(self):
                return "Example"

            @notion_property(column="Foo")
            async def foo(self):
                return "Foo"

        example = Example(property_types={})
        print(example.column_names_by_property_names)

    asyncio.run(main())


if __name__ == "__main__":
    test()
