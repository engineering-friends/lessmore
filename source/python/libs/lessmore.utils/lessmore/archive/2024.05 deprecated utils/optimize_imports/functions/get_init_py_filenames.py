import os
import re

from lessmore.utils.list_files import list_files
from lessmore.utils.optimize_imports.functions.iter_between_dirs import iter_between_dirs


def get_init_py_filenames(root_dir):
    """Get all __init__.py paths where we will create __init__.py file"""

    # - Get dirs and python_files

    dirs = [root for root, _, _ in os.walk(root_dir)]
    python_filenames = list_files(path=root_dir, pattern="*.py")

    # - Filter non-system directories

    dirs = [
        dir
        for dir in dirs
        if all(
            not re.match(exclude_pattern, dir + "/")
            for exclude_pattern in (
                ".*/\..*",  # exclude: /.git, /.idea, /.venv, etc
                ".*/tests/.*",
                ".*/archive/.*",
                ".*/__pycache__/.*",
            )
        )
    ]

    # - Filter where there is a parent __init__.py

    dirs = [
        dir
        for dir in dirs
        if any(
            os.path.exists(os.path.join(subdir, "__init__.py"))
            for subdir in iter_between_dirs(root_dir=root_dir, dir=dir)
        )
    ]

    # - Filter __no_init__.py present

    dirs = [dir for dir in dirs if not os.path.exists(os.path.join(dir, "__no_init__.py"))]

    # - Filter where there is a python file downstream

    dirs = [
        dir
        for dir in dirs
        if any(
            filename.startswith(dir + "/") and os.path.basename(filename) != "__init__.py"
            for filename in python_filenames
        )
    ]

    return [os.path.join(dir, "__init__.py") for dir in dirs]


def test():
    assert get_init_py_filenames("../test/my_module1") == [
        "../test/my_module1/__init__.py",
        "../test/my_module1/b_with_py_files/__init__.py",
    ]


if __name__ == "__main__":
    test()
