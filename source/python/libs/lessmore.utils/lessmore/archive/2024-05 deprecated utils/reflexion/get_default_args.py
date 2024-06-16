import inspect


def get_default_args(func):
    signature = inspect.signature(func)
    return {k: v.default for k, v in signature.parameters.items() if v.default is not inspect.Parameter.empty}


def test(sample=1):
    print(get_default_args(test))


if __name__ == "__main__":
    test()
