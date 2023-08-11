from pathlib import Path

from lessmore.utils.path_helpers.get_caller_filename import get_caller_path


def get_current_path() -> Path:
    return Path(get_caller_path())


def test():
    assert str(get_current_path().name) == "get_current_path.py"


if __name__ == "__main__":
    test()
