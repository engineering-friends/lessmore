from pathlib import Path
from typing import Any, Callable, Union


def write_file(
    data: Any,
    filename: Union[str, Path],
    as_bytes: bool = False,
    writer: Callable = lambda data, file: file.write(data),
    open_kwargs: dict = {},
) -> Any:
    """Write data to file_filename using writer function.

    Parameters
    ----------
    filename : Union[str, Path]
        filename to file.
    data : Any
        Data to write.
    as_bytes : bool, optional
        Whether to write as bytes, by default False
    writer : Callable, optional
        Writer function, by default lambda f, data: f.write(data)
    open_kwargs
        Additional arguments for open function.
    """
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
