from typing import Optional

import pytest

from lessmore.utils.configure_loguru.configure_loguru import configure_loguru
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

    # - Run tests
    pytest.main(
        args=[
            path or get_parent_frame_path(),
            f"--inline-snapshot={','.join(flags)}",
            "--capture=no",  # disables capturing of print calls
            "--log-cli-level=INFO",  # enables "live logs": logging records are shown immediately as they happen
            "--disable-warnings",
        ]
    )
