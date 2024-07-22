import asyncio
import inspect
import json
import time

from dataclasses import dataclass
from typing import Any

from inline_snapshot import snapshot
from lessmore.utils.asynchronous.gather_nested import gather_nested
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests
from notion_database_ai.field.auto_column import auto_column
from notion_database_ai.field.column import column
from notion_database_ai.field.extract_columns import extract_columns


async def build_notion_page(row: Any, property_types: dict):
    # - Extract columns

    columns = extract_columns(row=row)

    # - Assert all column names are present in notion page

    for _column in columns:
        assert _column.name in property_types, f"Property {_column.name} is not present"

    # - Build notion page

    properties = {_column.name: {} for _column in columns}
    page = {"properties": properties}

    for _column in columns:
        value = await getattr(row, _column.attribute) if _column.is_auto else getattr(row, _column.attribute)

        if property_types[_column.name] == "title":
            properties[_column.name][property_types[_column.name]] = [{"text": {"content": value}}]
        elif property_types[_column.name] == "number":
            properties[_column.name][property_types[_column.name]] = value
        elif property_types[_column.name] == "checkbox":
            properties[_column.name][property_types[_column.name]] = value
        elif property_types[_column.name] == "rich_text":
            properties[_column.name][property_types[_column.name]] = [{"text": {"content": value}}]
        elif property_types[_column.name] == "select":
            properties[_column.name][property_types[_column.name]] = {"name": value}
        elif property_types[_column.name] == "multi_select":
            properties[_column.name][property_types[_column.name]] = [{"name": x} for x in value]
        else:
            raise Exception(f"Unknown property type: {property_types[_column.name]}")

    # - Return page

    return page


def test():
    async def main():
        @dataclass
        class Example:
            title: str
            my_number: int = column(alias="My Number")

            @auto_column
            async def name(self):
                return "Example"

            @auto_column(alias="Foo")
            async def foo(self):
                return "Foo"

        assert await build_notion_page(
            Example(title="Example", my_number=123),
            property_types={
                "title": "title",
                "My Number": "number",
                "name": "rich_text",
                "Foo": "rich_text",
            },
        ) == snapshot(
            {
                "properties": {
                    "title": [{"text": {"content": "Example"}}],
                    "My Number": 123,
                    "Foo": [{"text": {"content": "Foo"}}],
                    "name": [{"text": {"content": "Example"}}],
                }
            }
        )

    asyncio.run(main())


if __name__ == "__main__":
    # test()
    run_snapshot_tests()
