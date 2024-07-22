import inspect

from dataclasses import dataclass
from typing import Any

from inline_snapshot import snapshot
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests
from notion_database_ai.field.auto_column import auto_column
from notion_database_ai.field.column import column


def extract_columns(value: Any) -> dict:
    # - Init result

    columns = {}

    # - Extract fields

    for field_name, field in value.__dataclass_fields__.items():
        columns[field_name] = {"attribute": field_name, **field.metadata.get("column", {})}

    # - Extract auto_columns

    # -- Collect

    for attr_name in dir(value):
        attribute = getattr(value, attr_name)
        if inspect.isawaitable(attribute):
            # close coroutine, it's not awaited
            attribute.close()

    # -- Add

    columns.update(value.auto_columns)

    # - Return

    return columns


def test():
    @dataclass
    class Example:
        title: str
        my_number: int = column(alias="MyNumber")

        @auto_column
        async def name(self):
            return "Example"

        @auto_column(alias="Foo")
        async def foo(self):
            return "Foo"

    assert extract_columns(Example(title="123", my_number=123)) == snapshot(
        {
            "title": {"attribute": "title"},
            "my_number": {"attribute": "my_number", "alias": "MyNumber", "is_auto": False},
            "foo": {"attribute": "foo", "alias": "Foo", "is_auto": True},
            "name": {"attribute": "name", "alias": None, "is_auto": True},
        }
    )


if __name__ == "__main__":
    run_snapshot_tests()
