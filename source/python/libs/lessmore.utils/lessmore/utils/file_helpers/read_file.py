from typing import Literal, Union


def read_file(filename: str, mode: Literal["r", "rb"] = "r") -> Union[str, bytes]:
    with open(filename, mode=mode) as file:
        return file.read()


def test():
    with open(__file__, mode="r") as file:
        content = file.read()

    assert read_file(__file__) == content


if __name__ == "__main__":
    test()
