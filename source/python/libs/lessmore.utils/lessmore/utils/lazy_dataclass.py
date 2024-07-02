import inspect

from dataclasses import dataclass, field
from typing import Any, Callable, Type, Union


def lazy_dataclass(cls):
    """Lazy evaluation of dataclass attributes when they are accessed."""
    cls = dataclass(cls)

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)

        if (
            not item.startswith("_")
            and callable(value)
            and not inspect.ismethod(value)
            and len(inspect.signature(value).parameters) == 1
            and "self" in inspect.signature(value).parameters
        ):
            value = value(self=self)
            setattr(self, item, value)
        return value

    cls.__getattribute__ = __getattribute__
    return cls


def test():
    @lazy_dataclass
    class Foo1:
        x: str
        xx: str = ""
        xxx: Union[str, Callable] = lambda self: self.x + self.x + self.x
        xxxx = lambda **kwargs: True

    @lazy_dataclass
    class Foo2(Foo1):
        xx: Union[str, Callable] = lambda self: self.x + self.x

    foo1 = Foo1(x="x")
    assert foo1.x == "x"
    assert foo1.xx == ""
    assert foo1.xxx == "xxx"

    foo2 = Foo2(x="x")
    assert foo2.x == "x"
    assert foo2.xx == "xx"
    assert foo2.xxx == "xxx"


if __name__ == "__main__":
    test()
