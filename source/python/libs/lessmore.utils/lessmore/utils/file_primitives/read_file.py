import os.path

from pathlib import Path
from typing import Any, Callable, Union


def read_file(
    filename: Union[str, Path],
    as_bytes: bool = False,
    reader: Callable = lambda file: file.read(),
    default: Any = None,  # if file does not exist
    open_kwargs: dict = {},  # extra kwargs for open
) -> Any:
    """A simple file reader helper, as it should have been in the first place. Useful for one-liners and nested function calls."""

    # - Convert Path to str

    filename = str(filename)

    # - Check if file exists

    if not os.path.exists(filename):
        return default

    # - Read file

    with open(filename, "rb" if as_bytes else "r", **open_kwargs) as file:
        return reader(file)


def test():
    print(read_file(filename="read_file.py")[:5])
    print(read_file(filename="read_file.py", as_bytes=True)[:5])


if __name__ == "__main__":
    test()
