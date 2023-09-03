from pathlib import Path

from lessmore.utils.path_helpers.test_get_frame_path.f2 import f2


def f3(frame_num: int) -> Path:
    return f2(frame_num=frame_num)
