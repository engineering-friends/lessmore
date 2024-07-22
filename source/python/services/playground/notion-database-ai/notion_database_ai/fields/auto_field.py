import asyncio
import inspect
import time

from functools import wraps
from typing import Coroutine, Optional

from lessmore.utils.asynchronous.async_cached_property import async_cached_property


class auto_field:
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
        # - Set column name inside the instance

        auto_fields = getattr(instance, "auto_fields", {})
        auto_fields[self.coroutine.__name__] = {"alias": self.alias}
        setattr(instance, "auto_fields", auto_fields)

        # - Return async property

        return async_cached_property(coroutine=self.coroutine).__get__(instance, owner)


def test():
    async def main():
        class Example:
            @auto_field
            def foo(self) -> str:
                return "foo"

            @auto_field(alias="asdf")
            async def bar(self) -> int:
                return 123

        example = Example()
        example.foo.close()
        example.bar.close()
        print(example.auto_fields)

    asyncio.run(main())


if __name__ == "__main__":
    test()
