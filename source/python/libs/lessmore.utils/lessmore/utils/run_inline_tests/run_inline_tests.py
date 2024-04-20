import logging
import os

from typing import Literal, Optional

import inline_snapshot
import pytest

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru
from lessmore.utils.file_utils.read_file import read_file
from lessmore.utils.file_utils.write_file import write_file
from lessmore.utils.get_frame_path.get_frame_path import get_parent_frame_path


def run_inline_tests(
    path: Optional[str] = None,
    mode: Literal["disabled", "create_missing", "fix_broken", "update_all"] = "create_missing",
):
    """Run test with inline snapshots.

    Parameters
    ----------
    path : str, optional
        Path to the file to run tests from. If not provided, the current file is used.
    """

    # - Assert inline_snapshot is ^0.8.0

    assert (
        inline_snapshot.__version__ == "0.8.0-marklidenberg-1.0.0"
    ), "Works only with https://github.com/marklidenberg/inline-snapshot"

    # - Configure loguru

    configure_loguru()

    # - Collect flags

    flags = []

    if mode == "create_missing":
        flags = ["create"]
    elif mode == "fix_broken":
        flags = ["create", "fix"]
    elif mode == "update_all":
        flags = ["create", "fix", "update", "trim"]
    elif mode == "disabled":
        pass
    else:
        raise Exception(f"Unknown mode: {mode}. Use one of ['disabled', 'create_missing', 'fix_broken', 'update_all']")

    # - Disable ugly logs from inline_snapshot

    class _Filter(logging.Filter):
        def filter(self, record):
            return not record.module.startswith("_")

    logging.getLogger().addFilter(_Filter())

    # - Create `conftest.py` file with hook to show traceback on failures

    # todo later: put into a plugin [@marklidenberg]

    old_contents = read_file("conftest.py", default="")

    write_file(
        filename="conftest.py",
        data="\n".join([old_contents, read_file(os.path.join(os.path.dirname(__file__), "default_conftest.py"))]),
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
            # "--no-summary",  # inline-snapshot works ONLY with the summary
            "--tb=no",
            "--quiet",  # even less noise
        ]
    )

    # - Restore old conftest.py

    os.remove("conftest.py")
    if old_contents:
        write_file(filename="conftest.py", data=old_contents)
