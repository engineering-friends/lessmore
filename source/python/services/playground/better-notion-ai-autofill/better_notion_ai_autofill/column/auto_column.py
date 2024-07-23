import asyncio
import inspect
import time

from functools import wraps
from typing import Coroutine, Optional

from lessmore.utils.asynchronous.async_cached_property import async_cached_property

from better_notion_ai_autofill.column.column_info import ColumnInfo


AUTO_COLUMN_INFOS = "auto_column_infos"


class auto_column:
    def __init__(
        self,
        coroutine: Optional[Coroutine] = None,
        alias: Optional[str] = None,
    ):
        self.coroutine = coroutine
        self.alias = alias

    def __call__(self, coroutine):
        # hack to use both @auto_field and @auto_field(column='...') decorators
        self.coroutine = coroutine
        return self

    def __get__(self, instance, owner):
        if instance is None:
            # - Init class

            auto_column_infos = getattr(owner, AUTO_COLUMN_INFOS, [])
            auto_column_infos.append(
                ColumnInfo(
                    attribute=self.coroutine.__name__,
                    alias=self.alias,
                    is_auto=True,
                )
            )
            setattr(owner, AUTO_COLUMN_INFOS, auto_column_infos)
        else:
            # - Init instance method

            return async_cached_property(coroutine=self.coroutine).__get__(instance, owner)


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
        Example.foo, Example.bar
        assert Example.auto_column_infos == [
            ColumnInfo(attribute="foo", alias=None, is_auto=True),
            ColumnInfo(attribute="bar", alias="asdf", is_auto=True),
        ]

    asyncio.run(main())


if __name__ == "__main__":
    test()
