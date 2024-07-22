import asyncio
import inspect
import time

from functools import wraps
from typing import Coroutine, Optional

from lessmore.utils.asynchronous.async_cached_property import async_cached_property
from notion_database_ai.column.column import Column


AUTO_COLUMNS = "auto_columns"


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

            auto_columns = getattr(owner, AUTO_COLUMNS, [])
            auto_columns.append(
                Column(
                    attribute=self.coroutine.__name__,
                    alias=self.alias,
                    is_auto=True,
                )
            )
            setattr(owner, AUTO_COLUMNS, auto_columns)
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

        example = Example()
        example.foo.close()
        example.bar.close()
        print(example.auto_columns)

    asyncio.run(main())


if __name__ == "__main__":
    test()
