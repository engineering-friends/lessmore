import logging
import os
import sys

from typing import Literal, Optional

import inline_snapshot
import pytest

from lessmore.utils.file_primitives.read_file import read_file
from lessmore.utils.file_primitives.write_file import write_file
from lessmore.utils.get_frame_path.get_frame_path import get_parent_frame_path
from lessmore.utils.loguru_utils.formatters.format_as_colored_json.format_as_colored_json import format_as_colored_json
from lessmore.utils.run_snapshot_tests.fixed_snapshot import fixed_snapshot
from loguru import logger


def run_snapshot_tests(
    path: Optional[str] = None,
    mode: Literal["assert", "create_missing", "fix_broken", "update_all"] = "create_missing",
) -> None:
    """Run test with inline snapshots.

    A helper over inline-snapshot library with better interface + prettier logs.

    Parameters
    ----------
    path : str, optional
        Path to the file to run tests from. If not provided, the current file is used.
    """

    # - Monkey patch inline_snapshot.snapshot

    inline_snapshot.snapshot.func.__code__ = fixed_snapshot.func.__code__

    # - Send warning if inline_snapshot version is not tested

    if inline_snapshot.__version__ != "0.8.0":
        logger.warning(
            f"inline_snapshot version is not tested: {inline_snapshot.__version__}. The only tested version is 0.8.0"
        )

    # - Log warning if ran from __init__.py file

    if not path and str(get_parent_frame_path()).endswith("__init__.py"):
        logger.warning("Snapshot tests don't run from `__init__.py` files (investigation needed)")

    # - Configure loguru

    logger.remove()
    logger.add(sink=sys.stdout, level="DEBUG", format=format_as_colored_json(append_non_json_traceback=True))

    # - Collect flags

    if mode == "assert":
        flags = []
    elif mode == "create_missing":
        flags = ["create"]
    elif mode == "fix_broken":
        flags = ["create", "fix"]
    elif mode == "update_all":
        flags = ["create", "fix", "update", "trim"]
    else:
        raise Exception(f"Unknown mode: {mode}. Use one of ['assert', 'create_missing', 'fix_broken', 'update_all']")

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
            "--no-header",
            # "--no-summary",  # inline-snapshot works ONLY with the summary
            "--tb=no",  # disable traceback in the summary
            "--quiet",  # even less noise
        ]
    )

    # - Restore old conftest.py

    os.remove("conftest.py")
    if old_contents:
        write_file(filename="conftest.py", data=old_contents)
