import asyncio
import inspect
import time

from functools import wraps
from typing import Coroutine, Optional

from lessmore.utils.asynchronous.async_cached_property import async_cached_property


class auto_property:
    def __init__(
        self,
        coroutine: Optional[Coroutine] = None,
        name: Optional[str] = None,
    ):
        self.coroutine = coroutine
        self.name = name or coroutine.__name__

    def __call__(self, coroutine):
        # hack to use both @notion_property and @notion_property(column='...') decorators
        self.coroutine = coroutine
        return self

    def __get__(self, instance, owner):
        # - Set column name inside the instance

        auto_property_name_to_attribute_name = getattr(instance, "auto_property_name_to_attribute_name", {})
        auto_property_name_to_attribute_name[self.name] = self.coroutine.__name__
        setattr(instance, "auto_property_name_to_attribute_name", auto_property_name_to_attribute_name)

        # - Return async property

        return async_cached_property(coroutine=self.coroutine).__get__(instance, owner)


def test():
    async def main():
        class Example:
            @auto_property(name="asdf")
            async def data(self):
                await asyncio.sleep(0.001)  # Simulate a long-running calculation
                return time.time()

        example = Example()
        example.data.close()
        print(example.auto_property_name_to_attribute_name)

    asyncio.run(main())


if __name__ == "__main__":
    test()