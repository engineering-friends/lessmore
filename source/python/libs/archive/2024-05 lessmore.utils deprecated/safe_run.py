def safe_run(func, default=None, args=None, kwargs=None):
    args = args or ()
    kwargs = kwargs or {}

    try:
        return func(*args, **kwargs)
    except:
        if callable(default):
            return default()
        else:
            return default


def test():
    assert safe_run(func=lambda: 1, default=2) == 1
    assert safe_run(func=lambda: 1 / 0, default=2) == 2


if __name__ == "__main__":
    test()
