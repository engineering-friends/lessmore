import pytest

from inline_snapshot import snapshot

from lessmore.utils.file_helpers.read_file import read_file
from lessmore.utils.file_helpers.write_file import write_file
from lessmore.utils.get_frame_path.get_frame_path import get_frame_path, get_parent_frame_path


class SnapshotUpdateOptions:
    ALL = "all"
    NEW = "new"
    FAILING = "failing"
    NONE = "none"


def run_inline_snapshot_tests(mode: str = SnapshotUpdateOptions.NEW) -> None:
    """
    Parameters
    ----------

    mode : SnapshotUpdateOptions, optional
        The mode to run the inline snapshot tests in, by default 'new'

        - 'all': update all snapshots
        - 'new': update new snapshots
        - 'failing': update failing snapshots
        - 'none': do not update snapshots

    Default usage:
    run_inline_snapshot_tests(SnapshotUpdateOptions.NEW)
    # run_inline_snapshot_tests(SnapshotUpdateOptions.ALL)

    """
    pytest.main(
        args=[
            str(get_parent_frame_path()),
            f"--update-snapshots={mode}",
        ]
    )


# - Test


def test_something():
    assert 1 == snapshot(1)  # filled automatically


def run_test():
    # - Run test

    run_inline_snapshot_tests(SnapshotUpdateOptions.NEW)

    # - Assert it worked

    assert "snapshot(1)" in read_file(__file__)


if __name__ == "__main__":
    run_test()
