import asyncio
import inspect
import json

from lessmore.utils.asynchronous.async_cached_property import async_cached_property
from notion_database_ai.auto_column import auto_column
from notion_database_ai.column import column


class DatabaseRow:
    def __init__(self, property_types: dict, **kwargs):
        self.property_types = property_types
        self.auto_column_names_by_property_names = {}  # column names are set from notion_property on first descriptor call

        super().__init__(**kwargs)

        # - Get each property at least once to ensure that metadata is loaded for "notion_properties"

        for attr_name in dir(self):
            coroutine = getattr(self, attr_name)
            if inspect.isawaitable(coroutine):
                # close the coroutine that is not awaited
                coroutine.close()

    def get_column_names(self):
        result = []

        # add dataclass fields

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
        class Example(DatabaseRow):
            title: str
            my_number: str = column(name="My Number")

            @auto_column
            async def name(self):
                return "Example"

            @auto_column(name="Foo")
            async def foo(self):
                return "Foo"

        example = Example(property_types={})
        print(example.auto_column_names_by_property_names)

    asyncio.run(main())


if __name__ == "__main__":
    test()
