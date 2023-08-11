def get_complex_attribute(value, expression, default=None):
    if isinstance(expression, list):
        for sub_expression in expression:
            res = get_complex_attribute(value, sub_expression)
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

    print(get_complex_attribute(np, "random"))
    print(get_complex_attribute(np, "random.choice"))
    print(get_complex_attribute(np, "random.choice"))
    print(get_complex_attribute(np, "rand.choice", default="Default"))

    try:
        print(get_complex_attribute(np, "rand.choice"))
    except:
        print("Attribute not found")


if __name__ == "__main__":
    test()
