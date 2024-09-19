import os

from pathlib import Path
from typing import Any, Callable, Union


def write_file(
    data: Any,
    filename: Union[str, Path],
    as_bytes: bool = False,
    writer: Callable = lambda data, file: file.write(data),
    open_kwargs: dict = {},
    ensure_path: bool = True,
) -> Any:
    """A simple file writer helper, as it should have been in the first place. Useful for one-liners or nested function calls."""

    # - Ensure path

    if ensure_path:
        os.makedirs(os.path.dirname(str(filename)), exist_ok=True)

    # - Write file

    with open(str(filename), "wb" if as_bytes else "w", **open_kwargs) as file:
        return writer(data, file)


def test():
    filename = "test.txt"
    data = "test"
    write_file(filename=filename, data=data)

    assert open(filename, "r").read() == data

    import os

    os.remove(filename)


if __name__ == "__main__":
    test()
