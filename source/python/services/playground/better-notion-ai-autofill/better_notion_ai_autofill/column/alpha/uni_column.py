import asyncio
import inspect
import time

from dataclasses import MISSING, Field, dataclass
from functools import wraps
from typing import Any, Coroutine, Optional

from better_notion_ai_autofill.column.column_info import ColumnInfo
from lessmore.utils.asynchronous.async_cached_property import async_cached_property


AUTO_COLUMN_INFOS = "auto_column_infos"

import asyncio
import inspect
import time

from dataclasses import MISSING, Field, dataclass
from functools import wraps
from typing import Any, Coroutine, Optional

from better_notion_ai_autofill.column.column_info import ColumnInfo


""" My attempt to make a single decorator for both static and autofilled fields. 

Failed to do so, as both dataclass have strict behavior for annotations. Some other way needed

"""


def database_row(cls):
    """A workaround to use single column decorator for both static and autofilled fields. Adds annotations for autofilled properties, otherwise dataclass will fail."""
    cls.__annotations__ = {name: Any for name in cls.__dict__ if isinstance(cls.__dict__[name], uni_column)}
    cls = dataclass(cls)
    return cls


def test():
    async def main():
        @database_row
        class Example:
            title: str
            my_number: int = uni_column(alias="MyNumber")

            @uni_column
            async def name(self) -> str:
                return "Example"

            @uni_column(alias="Foo")
            async def foo(self):
                return "Foo"

        assert Example.auto_column_infos == [
            ColumnInfo(attribute="name", alias=None, is_auto=True),
            ColumnInfo(attribute="foo", alias="Foo", is_auto=True),
        ]

    asyncio.run(main())


if __name__ == "__main__":
    test()


class uni_column(async_cached_property, Field):
    def __init__(
        self,
        coroutine: Optional[Coroutine] = None,
        alias: Optional[str] = None,
    ):
        self.coroutine = coroutine
        self.alias = alias

        async_cached_property.__init__(
            self=self,
            coroutine=self.coroutine,
        )
        Field.__init__(  # default arguments of field(...)
            self=self,
            default=MISSING,
            default_factory=MISSING,
            init=True,
            repr=True,
            hash=None,
            compare=True,
            metadata={"column_info": ColumnInfo(alias=alias)},
            kw_only=MISSING,
        )

    def __call__(self, coroutine):
        # hack to use both @auto_field and @auto_field(column='...') decorators
        self.coroutine = coroutine
        return self

    def __set_name__(self, cls: Any, name: str):
        if self.coroutine:
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
        @database_row
        class Example:
            title: str
            my_number: int = uni_column(alias="MyNumber")

            @uni_column
            async def name(self) -> str:
                return "Example"

            @uni_column(alias="Foo")
            async def foo(self):
                return "Foo"

        # access properties to trigger auto_column.__get__
        print(Example.auto_column_infos)
        # assert Example.auto_column_infos == [
        #     ColumnInfo(attribute="name", alias=None, is_auto=True),
        #     ColumnInfo(attribute="foo", alias="Foo", is_auto=True),
        # ]

    asyncio.run(main())


if __name__ == "__main__":
    test()
