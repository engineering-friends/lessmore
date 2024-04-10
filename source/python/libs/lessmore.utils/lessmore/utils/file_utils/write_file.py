from typing import Any, Callable


def write_file(
    data: Any,
    path: str,
    as_bytes: bool = False,
    writer: Callable = lambda data, file: file.write(data),
    **kwargs,
) -> Any:
    """Write data to file_path using writer function.

    Parameters
    ----------
    path : str
        Path to file.
    data : Any
        Data to write.
    as_bytes : bool, optional
        Whether to write as bytes, by default False
    writer : Callable, optional
        Writer function, by default lambda f, data: f.write(data)
    """
    with open(path, "wb" if as_bytes else "w", **kwargs) as file:
        return writer(data, file)


def test():
    file_path = "test.txt"
    data = "test"
    write_file(path=file_path, data=data)

    assert open(file_path, "r").read() == data

    import os

    os.remove(file_path)


if __name__ == "__main__":
    test()
