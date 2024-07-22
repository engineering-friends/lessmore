from pathlib import Path

from lessmore.utils.file_primitives.local_path.local_path import local_path


def test():
    assert local_path("test").endswith("local_path/test_local_path/test")
    assert str(local_path(Path("test"))).endswith("local_path/test_local_path/test")


if __name__ == "__main__":
    test()
