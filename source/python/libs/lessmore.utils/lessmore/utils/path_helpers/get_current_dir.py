from pathlib import Path

from lessmore.utils.path_helpers.get_caller_path import get_caller_path


def get_current_dir() -> Path:
    return Path(get_caller_path()).parent


def test():
    assert str(get_current_dir().name) == "path_helpers"


if __name__ == "__main__":
    test()
