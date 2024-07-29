import sys


def get_traceback(exception, engine: str = "better_exceptions") -> str:
    assert engine in ["stackprinter", "better_exceptions"]

    if engine == "better_exceptions":
        import better_exceptions

        return "".join(better_exceptions.format_exception(*exception))
    elif engine == "stackprinter":
        import stackprinter

        return stackprinter.format(exception)


def test():
    try:
        raise Exception("test")
    except Exception as e:
        print(get_traceback(exception=sys.exc_info(), engine="stackprinter"))
        print(get_traceback(exception=sys.exc_info(), engine="better_exceptions"))


if __name__ == "__main__":
    test()
