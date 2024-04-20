import os.path

from typing import Any, Callable


def read_file(
    filename: str,
    as_bytes: bool = False,
    reader: Callable = lambda file: file.read(),
    default=None,
    **kwargs,
) -> Any:
    """Чтение файла.

    Parameters
    ----------
    filename : str
        Путь к файлу.
    as_bytes : bool, optional
        Читать файл как байты, by default False
    reader : Callable, optional
        Функция чтения файла, by default lambda f: f.read()
    """

    # - Return default if file doesn't exist

    if not os.path.exists(filename):
        return default

    # - Read file

    with open(filename, "rb" if as_bytes else "r", **kwargs) as file:
        return reader(file)


def test():
    print(read_file(filename="read_file.py")[:5])
    print(read_file(filename="read_file.py", as_bytes=True)[:5])


if __name__ == "__main__":
    test()
