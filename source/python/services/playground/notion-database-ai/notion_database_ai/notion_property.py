import asyncio
import inspect
import time

from functools import wraps
from typing import Coroutine, Optional

from lessmore.utils.asynchronous.async_cached_property import async_cached_property


class notion_property:
    def __init__(
        self,
        coroutine: Optional[Coroutine] = None,
        column: Optional[str] = None,
    ):
        self.coroutine = coroutine
        self.column = column or coroutine.__name__

    def __call__(self, coroutine):
        # hack to use both @notion_property and @notion_property(column='...') decorators
        self.coroutine = coroutine
        return self

    def __get__(self, instance, owner):
        # - Set column name inside owner

        column_names_by_property_names = getattr(owner, "__column_names_by_property_names", {})
        column_names_by_property_names[self.coroutine.__name__] = self.column
        setattr(owner, "column_names_by_property_names", column_names_by_property_names)

        # - Return async property

        return async_cached_property(coroutine=self.coroutine).__get__(instance, owner)


def test():
    async def main():
        class Example:
            @notion_property(column="asdf")
            async def data(self):
                await asyncio.sleep(0.001)  # Simulate a long-running calculation
                return time.time()

        example = Example()
        print(example.data)
        print(example.column_names_by_property_names)

    asyncio.run(main())


if __name__ == "__main__":
    test()
