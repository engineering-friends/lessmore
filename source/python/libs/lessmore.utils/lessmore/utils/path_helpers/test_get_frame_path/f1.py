from pathlib import Path

from lessmore.utils.path_helpers.get_frame_path import get_frame_path


def f1(frame_num: int) -> Path:
    return get_frame_path(frame_num=frame_num)
