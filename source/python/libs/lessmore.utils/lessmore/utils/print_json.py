import json


def print_json(obj, default=str, **kwargs):
    print(json.dumps(obj, default=default, **kwargs))


def test():
    print_json({"a": 1, "b": 2})


if __name__ == "__main__":
    test()
