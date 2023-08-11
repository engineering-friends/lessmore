import os

from typing import Literal, Union


def write_file(filename: str, content: Union[str, bytes], mode: Literal["w", "wb", "a", "ab"] = "w") -> None:
    with open(filename, mode=mode) as file:
        file.write(content)


def test():
    # - Write file

    write_file(filename="test.txt", content="Hello World")

    # - Assert it worked

    with open("test.txt", mode="r") as file:
        content = file.read()

    assert content == "Hello World"

    # - Fix

    os.remove("test.txt")


if __name__ == "__main__":
    test()
