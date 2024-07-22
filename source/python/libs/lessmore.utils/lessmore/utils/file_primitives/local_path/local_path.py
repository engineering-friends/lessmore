import os.path

from pathlib import Path
from typing import Union

from lessmore.utils.get_frame_path.get_frame_path import get_parent_frame_path


def local_path(path: Union[str, os.PathLike, Path]) -> str:
    """Helper to quickly get a local path relative to the caller's file."""
    if isinstance(path, Path):
        return os.path.dirname(get_parent_frame_path()) / path
    else:
        return os.path.join(os.path.dirname(get_parent_frame_path()), str(path))
