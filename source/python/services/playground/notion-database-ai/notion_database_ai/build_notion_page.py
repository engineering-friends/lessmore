import asyncio
import inspect
import json

from dataclasses import dataclass
from typing import Any

from lessmore.utils.asynchronous.gather_nested import gather_nested
from notion_database_ai.columns.auto_property import auto_property
from notion_database_ai.columns.input_property import input_property


async def build_notion_page(row: Any, property_types: dict):
    # - Get column_name_by_attribute_name

    property_name_to_attribute_name = {}

    # -- Go through fields first

    for field_name, field in row.__dataclass_fields__.items():
        if "property_name" in field.metadata:
            property_name_to_attribute_name[field.metadata["property_name"]] = field_name
        else:
            property_name_to_attribute_name[field_name] = field_name

    # -- Go through all auto_properties

    # --- Collect auto properties

    for attr_name in dir(row):
        attr = getattr(row, attr_name)
        if inspect.isawaitable(attr):
            attr.close()

    # --- Add auto_properties

    property_name_to_attribute_name.update(row.auto_property_name_to_attribute_name)

    # - Assert all properties are in place

    assert set(property_name_to_attribute_name.keys()).issubset(
        set(property_types.keys())
    ), f"Notion page: {list(property_types.keys())}, your dataclass: {list(property_name_to_attribute_name.keys())}"

    # - Build notion page

    properties = {}
    page = {"properties": properties}

    for property_name, attribute_name in property_name_to_attribute_name.items():
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
