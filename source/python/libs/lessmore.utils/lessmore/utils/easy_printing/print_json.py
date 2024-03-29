import json


def print_json(obj, copy: bool = False, default=str, indent=1, ensure_ascii=False, **kwargs):
    # - Dumps

    s = json.dumps(obj, default=default, indent=indent, ensure_ascii=ensure_ascii, **kwargs)

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
