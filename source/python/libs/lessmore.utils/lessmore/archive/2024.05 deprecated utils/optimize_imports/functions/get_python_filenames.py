import os
import re

from lessmore.utils.list_files import list_files
from lessmore.utils.optimize_imports.functions.iter_between_dirs import iter_between_dirs


def get_python_filenames(root_dir):
    """Get all __init__.py paths where we will create __init__.py file"""

    # - Get dirs and python_files

    python_filenames = list_files(path=root_dir, filter_pattern="*.py")

    # - Filter non-system directories

    python_filenames = [
        python_filename
        for python_filename in python_filenames
        if all(
            not re.match(exclude_pattern, os.path.dirname(python_filename) + "/")
            for exclude_pattern in (
                ".*/\..*",  # exclude: /.git, /.idea, /.venv, etc
                ".*/tests/.*",
                ".*/archive/.*",
                ".*/test/.*",
                ".*/__pycache__/.*",
            )
        )
    ]

    # - Filter non-system files

    python_filenames = [
        python_filename for python_filename in python_filenames if os.path.basename(python_filename)[0] != "_"
    ]

    return python_filenames


def test():
    assert get_python_filenames("../test/my_module1") == [
        "../test/my_module1/a.py",
        "../test/my_module1/b_with_py_files/b.py",
        "../test/my_module1/d_no_init/d.py",
    ]


if __name__ == "__main__":
    test()
