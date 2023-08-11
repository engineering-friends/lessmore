import json


def print_json(value, default=str, copy: bool = False, **kwargs):
    # - Dump

    s = json.dumps(value, default=default, **kwargs)

    # - Copy

    if copy:
        import pyperclip

        pyperclip.copy(s)

    # - Print

    print(s)

    # - Return

    return s


def test():
    print_json({"a": 1, "b": 2})


if __name__ == "__main__":
    test()
