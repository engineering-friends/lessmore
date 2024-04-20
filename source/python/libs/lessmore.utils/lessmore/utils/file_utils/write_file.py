import os
import shutil

from typing import Any, Callable, Optional


def write_file(
    data: Any,
    filename: str,
    as_bytes: bool = False,
    writer: Callable = lambda data, file: file.write(data),
    backup: bool = False,
    backuper: Callable = lambda filename: shutil.copy(filename, filename + ".bak"),
    swap: bool = True,
    overwrite: bool = True,
    **kwargs,
) -> Any:
    """Write data to file_path using writer function.

    Parameters
    ----------
    filename : str
        Path to file.
    data : Any
        Data to write.
    as_bytes : bool, optional
        Whether to write as bytes, by default False
    writer : Callable, optional
        Writer function, by default lambda f, data: f.write(data)
    backup : bool, optional
        Whether to backup file, by default False
    backuper : Callable, optional
        Backuper function, by default lambda filename: shutil.copy(filename, filename + ".bak")
    swap : bool, optional
        Whether to swap file, by default False
    overwrite : bool, optional
        Whether to overwrite file, by default True

    # todo maybe: writer that accepts filename, like pd.to_csv? [@marklidenberg]
    """

    # - Make directory if not exists

    os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)

    # - Check if file exists

    if not overwrite and os.path.exists(filename):
        raise FileExistsError(f"File {filename} already exists")

    # - Backup if needed

    if backup and os.path.exists(filename):
        backuper(filename)

    # - Write file

    if not swap:
        with open(filename, "wb" if as_bytes else "w", **kwargs) as file:
            result = writer(data, file)
    else:
        with open(filename + ".tmp", "wb" if as_bytes else "w", **kwargs) as file:
            result = writer(data, file)
        os.replace(filename + ".tmp", filename)

    # - Return result

    return result


def test():
    file_path = "test.txt"
    data = "test"
    write_file(filename=file_path, data=data)

    assert open(file_path, "r").read() == data

    import os

    os.remove(file_path)
