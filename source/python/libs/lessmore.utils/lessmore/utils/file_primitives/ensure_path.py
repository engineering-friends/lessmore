import os

from pathlib import Path
from typing import Union


def ensure_path(path: Union[str, os.PathLike, Path]) -> Union[str, os.PathLike, Path]:
    """
    Ensure that the directory path exists.
    """
    os.makedirs(os.path.dirname(str(path)), exist_ok=True)
    return path


def test():
    ensure_path("/tmp/ensure_path/foo/zzz.txt")
    ensure_path("/tmp/ensure_path/bar/baz/")
    ensure_path("/tmp/ensure_path/bar/qux")

    assert os.path.exists("/tmp/ensure_path/foo")
    assert os.path.exists("/tmp/ensure_path/bar/baz")
    assert not os.path.exists("/tmp/ensure_path/bar/qux")


if __name__ == "__main__":
    test()
