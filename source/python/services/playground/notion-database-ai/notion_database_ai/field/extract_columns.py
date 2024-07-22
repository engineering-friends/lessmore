import inspect

from dataclasses import dataclass
from typing import Any

from inline_snapshot import snapshot
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests
from notion_database_ai.field.auto_column import auto_column
from notion_database_ai.field.column import Column, column


def extract_columns(row: Any) -> list:
    # - Init result

    columns = []

    # - Extract fields

    for field_name, field in row.__dataclass_fields__.items():
        # - Set values from metadata

        if "column" in field.metadata:
            _column = Column(
                attribute=field_name, **{k: v for k, v in field.metadata["column"].__dict__.items() if v is not None}
            )
        else:
            _column = Column(attribute=field_name)

        # - Add to result

        columns.append(_column)

    # - Extract auto_columns

    # -- Collect

    for attr_name in dir(row):
        attribute = getattr(row, attr_name)
        if inspect.isawaitable(attribute):
            # close coroutine, it's not awaited
            attribute.close()

    # -- Add

    columns += row.auto_columns

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
        [
            Column(attribute="title", alias=None, is_auto=False),
            Column(attribute="my_number", alias="MyNumber", is_auto=False),
            Column(attribute="foo", alias="Foo", is_auto=True),
            Column(attribute="name", alias=None, is_auto=True),
        ]
    )


if __name__ == "__main__":
    run_snapshot_tests(mode="update_all")
