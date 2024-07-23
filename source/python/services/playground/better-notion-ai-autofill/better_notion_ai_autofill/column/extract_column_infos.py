import inspect

from dataclasses import dataclass
from typing import Any

from inline_snapshot import snapshot
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests

from better_notion_ai_autofill.column.auto_column import auto_column
from better_notion_ai_autofill.column.column import column
from better_notion_ai_autofill.column.column_info import ColumnInfo


def extract_column_infos(cls: type) -> list:
    # - Init result

    column_infos = []

    # - Extract fields

    for field_name, field in cls.__dataclass_fields__.items():
        # - Set values from metadata

        if "column_info" in field.metadata:
            column_info = ColumnInfo(
                attribute=field_name,
                **{k: v for k, v in field.metadata["column_info"].__dict__.items() if v is not None},
            )
        else:
            column_info = ColumnInfo(attribute=field_name)

        # - Add to result

        column_infos.append(column_info)

    # - Extract auto_columns

    # -- Get attributes to trigger auto_column decorators

    for attr_name in dir(cls):
        if attr_name.startswith("__"):
            continue
        getattr(cls, attr_name)

    # -- Add

    column_infos += cls.auto_column_infos

    # - Return

    return column_infos


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

    assert extract_column_infos(Example) == snapshot(
        [
            ColumnInfo(attribute="title", alias=None, is_auto=False),
            ColumnInfo(attribute="my_number", alias="MyNumber", is_auto=False),
            ColumnInfo(attribute="foo", alias="Foo", is_auto=True),
            ColumnInfo(attribute="name", alias=None, is_auto=True),
        ]
    )


if __name__ == "__main__":
    run_snapshot_tests(mode="update_all")
