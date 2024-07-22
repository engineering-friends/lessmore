import asyncio
import inspect
import json

from dataclasses import dataclass
from typing import Any

from lessmore.utils.asynchronous.gather_nested import gather_nested
from notion_database_ai.get_properties_to_attribute_name import get_property_name_to_attribute_name
from notion_database_ai.properties.auto_property import auto_property
from notion_database_ai.properties.input_property import input_property


async def build_notion_page(row: Any, property_types: dict):
    # - Build notion page

    properties = {}
    page = {"properties": properties}

    for property_name, attribute_name in get_property_name_to_attribute_name(row).items():
        if property_types[property_name] == "title":
            properties[property_name] = [{"text": {"content": getattr(row, attribute_name)}}]
        elif property_types[property_name] == "number":
            properties[property_name] = getattr(row, attribute_name)
        elif property_types[property_name] == "checkbox":
            properties[property_name] = getattr(row, attribute_name)
        elif property_types[property_name] == "rich_text":
            properties[property_name] = [{"text": {"content": getattr(row, attribute_name)}}]
        elif property_types[property_name] == "select":
            properties[property_name] = {"name": getattr(row, attribute_name)}
        elif property_types[property_name] == "multi_select":
            properties[property_name] = [{"name": getattr(row, attribute_name)}]
        else:
            raise Exception(f"Unknown property type: {property_types[property_name]}")

    # - Await coroutines

    page = await gather_nested(page)

    # - Return page

    return page


def test():
    async def main():
        @dataclass
        class Example:
            title: str
            my_number: int = input_property(name="My Number")

            @auto_property
            async def name(self):
                return "Example"

            @auto_property(name="Foo")
            async def foo(self):
                return "Foo"

        print(
            await build_notion_page(
                Example(title="Example", my_number=123),
                property_types={
                    "title": "title",
                    "My Number": "number",
                    "name": "rich_text",
                    "Foo": "rich_text",
                },
            )
        )

    asyncio.run(main())


if __name__ == "__main__":
    test()
