from pathlib import Path
from typing import Iterable

import pytest

from pytest import ExitCode

from lessmore.utils.list_files import list_files


def run_tests(
    path: str = ".",
    excluded_dirs: Iterable = ("/.venv/", "/archive/", "/backlog/"),
    exclude_slow: bool = True,
):
    # - Get all python files

    path = Path(path)
    filenames = list_files(path, filter_pattern="*.py")
    filenames = [
        filename for filename in filenames if all(excluded_dir not in filename for excluded_dir in excluded_dirs)
    ]

    # - Run test for each file

    for filename in filenames:
        # - Prepare args

        args = [filename]
        if exclude_slow:
            args += ["-m", "not slow"]

        # - Run test

        assert int(pytest.main(args)) in [ExitCode.OK, ExitCode.NO_TESTS_COLLECTED]


if __name__ == "__main__":
    import fire

    fire.Fire(run_tests)
