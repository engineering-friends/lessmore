import os

from pathlib import Path


def get_current_working_dir() -> Path:
    return Path(os.getcwd())


def test():
    return str(get_current_working_dir()) == os.getcwd()


if __name__ == "__main__":
    test()
