import os

from typing import Literal, Union


def write_file(content: Union[str, bytes], filename: str, mode: Literal["w", "a"] = "w") -> None:
    # - Add bytes mode if needed

    if isinstance(content, bytes):
        mode += "b"

    # - Write file

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
