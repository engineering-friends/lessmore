import os

from pathlib import Path
from typing import Union


def ensure_path(path: Union[str, os.PathLike, Path], is_dir: bool = False) -> Union[str, os.PathLike, Path]:
    """Ensure that the directory path exists and return the path.

    Common scenario: `with open(ensure_path("path/to/file.txt"), "w") as f:...`

    """
    if is_dir:
        os.makedirs(str(path), exist_ok=True)
    else:
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
