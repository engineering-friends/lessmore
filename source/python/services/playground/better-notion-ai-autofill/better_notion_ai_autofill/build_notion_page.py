import asyncio
import inspect
import json
import time

from dataclasses import dataclass
from typing import Any, Optional

from inline_snapshot import snapshot
from lessmore.utils.asynchronous.gather_nested import gather_nested
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests
from loguru import logger

from better_notion_ai_autofill.column.auto_column import auto_column
from better_notion_ai_autofill.column.column import column
from better_notion_ai_autofill.column.extract_column_infos import extract_column_infos


async def build_notion_page(row: Any, property_types: dict):
    # - Extract columns

    column_infos = extract_column_infos(cls=row.__class__)

    # - Assert all column names are present in notion page

    for column_info in column_infos:
        assert column_info.name in property_types, f"Property {column_info.name} is not present"

    # - Build notion page

    properties = {column_info.name: {} for column_info in column_infos}
    page = {"properties": properties}

    for column_info in column_infos:
        value = (
            await getattr(row, column_info.attribute) if column_info.is_auto else getattr(row, column_info.attribute)
        )

        _type = property_types[column_info.name]
        property = properties[column_info.name]

        if _type == "title":
            property[_type] = [{"text": {"content": value}}]
        elif _type == "number":
            properties[column_info.name][_type] = value
        elif _type == "checkbox":
            properties[column_info.name][_type] = value
        elif _type == "rich_text":
            properties[column_info.name][_type] = [{"text": {"content": value}}]
        elif _type == "select":
            properties[column_info.name][_type] = {"name": value}
        elif _type == "multi_select":
            properties[column_info.name][_type] = [{"name": x} for x in value]
        else:
            raise Exception(f"Unknown property type: {_type}")

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
                    "title": {"title": [{"text": {"content": "Example"}}]},
                    "My Number": {"number": 123},
                    "Foo": {"rich_text": [{"text": {"content": "Foo"}}]},
                    "name": {"rich_text": [{"text": {"content": "Example"}}]},
                }
            }
        )

    asyncio.run(main())


if __name__ == "__main__":
    # test()
    run_snapshot_tests()
