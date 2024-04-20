import os

from typing import Optional

import pytest

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru
from lessmore.utils.file_utils.read_file import read_file
from lessmore.utils.file_utils.write_file import write_file
from lessmore.utils.get_frame_path.get_frame_path import get_parent_frame_path


@pytest.fixture(autouse=True)
def separate_tests():
    print("\n" + "─" * 88)
    yield
    print("\n")


def run_inline_tests(
    path: Optional[str] = None,
    create: bool = True,
    update: bool = False,
    fix: bool = False,
    trim: bool = False,
):
    """Run test with inline snapshots.

    Parameters
    ----------
    path : str, optional
        Path to the file to run tests from. If not provided, the current file is used.
    create : bool, optional
        creates snapshots which are currently not defined, see https://15r10nk.github.io/inline-snapshot/pytest/
    update : bool, optional
        update snapshots if they changed their representation (result of repr()), see https://15r10nk.github.io/inline-snapshot/pytest/
    fix : bool, optional
        change snapshots which are currently breaking your tests (where the result of the snapshot operation is False)., see https://15r10nk.github.io/inline-snapshot/pytest/
    trim : bool, optional
        changes the snapshot in a way which will make the snapshot more precise (see value in snapshot() and snapshot()[key]), see https://15r10nk.github.io/inline-snapshot/pytest/
    """

    # - Configure loguru

    configure_loguru()

    # - Collect flags

    flags = []
    if create:
        flags.append("create")
    if update:
        flags.append("update")
    if fix:
        flags.append("fix")
    if trim:
        flags.append("trim")

    # - Create `conftest.py` file with hook to show traceback on failures

    # todo later: put into a plugin [@marklidenberg]

    old_contents = read_file("conftest.py", default="")

    write_file(
        filename="conftest.py",
        data="\n".join(
            [
                old_contents,
                rf"""
import pytest
import sys

@pytest.hookimpl(tryfirst=True)
def pytest_exception_interact(node, call, report):
    if report.failed:
        print('\n', call.excinfo.getrepr(style='native'), file=sys.stderr)
        """.strip(),
            ]
        ),
    )

    # - Run tests

    pytest.main(
        args=[
            path or get_parent_frame_path(),
            f"--inline-snapshot={','.join(flags)}" if flags else "--inline-snapshot-disable",
            "--capture=no",  # disables capturing of print calls
            "--log-cli-level=INFO",  # enables "live logs": logging records are shown immediately as they happen
            "--disable-warnings",
            "--no-header",  # disables pytest header, like python version and stuff
            "--no-summary",  # disables post-tests summary
        ]
    )

    # - Restore old conftest.py

    os.remove("conftest.py")
    if old_contents:
        write_file(filename="conftest.py", data=old_contents)
