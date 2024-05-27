from typing import Any


def get_nested_attr(value, expression: str, default: Any = None):
    if isinstance(expression, list):
        for sub_expression in expression:
            res = get_nested_attr(value, sub_expression)
            if res is not None:
                return res
    else:
        try:
            for attribute in expression.split("."):
                value = getattr(value, attribute)
            return value
        except:
            pass

    return default


def test():
    import numpy as np

    print(get_nested_attr(np, expression="random"))
    print(get_nested_attr(np, expression="random.choice"))
    print(get_nested_attr(np, expression="non.existent", default="some_default"))


if __name__ == "__main__":
    test()
