import os


def iter_between_dirs(root_dir, dir):
    """Iterate paths between root_dir and dir (including root_dir and dir)"""

    root_dir = os.path.abspath(root_dir)
    dir = os.path.abspath(dir)

    assert dir.startswith(root_dir)

    dir = dir[len(root_dir) + 1 :]
    dir = dir.split("/")

    for i in range(len(dir) + 1):
        yield os.path.join(root_dir, *dir[:i])


def test():
    assert list(iter_between_dirs("/a/b", "/a/b/c/d")) == ["/a/b", "/a/b/c", "/a/b/c/d"]


if __name__ == "__main__":
    test()
