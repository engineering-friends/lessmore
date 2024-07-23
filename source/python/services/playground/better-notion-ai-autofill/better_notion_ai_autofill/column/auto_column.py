import asyncio
import inspect
import time

from functools import wraps
from typing import Any, Coroutine, Optional

from lessmore.utils.asynchronous.async_cached_property import async_cached_property

from better_notion_ai_autofill.column.column_info import ColumnInfo


AUTO_COLUMN_INFOS = "auto_column_infos"


class auto_column(async_cached_property):
    def __init__(
        self,
        coroutine: Optional[Coroutine] = None,
        alias: Optional[str] = None,
    ):
        self.coroutine = coroutine
        self.alias = alias

        super().__init__(coroutine=self.coroutine)

    def __call__(self, coroutine):
        # hack to use both @auto_field and @auto_field(column='...') decorators
        self.coroutine = coroutine
        return self

    def __set_name__(self, cls: Any, name: str):
        auto_column_infos = getattr(cls, AUTO_COLUMN_INFOS, [])
        auto_column_infos.append(
            ColumnInfo(
                attribute=self.coroutine.__name__,
                alias=self.alias,
                is_auto=True,
            )
        )
        setattr(cls, AUTO_COLUMN_INFOS, auto_column_infos)


def test():
    async def main():
        class Example:
            @auto_column
            def foo(self) -> str:
                return "foo"

            @auto_column(alias="asdf")
            async def bar(self) -> int:
                return 123

        # access properties to trigger auto_column.__get__
        assert Example.auto_column_infos == [
            ColumnInfo(attribute="foo", alias=None, is_auto=True),
            ColumnInfo(attribute="bar", alias="asdf", is_auto=True),
        ]

    asyncio.run(main())


if __name__ == "__main__":
    test()
