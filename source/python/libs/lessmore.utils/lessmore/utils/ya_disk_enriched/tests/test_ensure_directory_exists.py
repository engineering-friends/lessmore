import os

from pathlib import Path

import pytest

from lessmore.utils.ya_disk_enriched.tests.init_test_client import init_client


@pytest.mark.slow
def test_ensure_directory_exists():
    # - Init client

    client = init_client()

    # - Init test path

    remote_dir = Path("/test-ya-disk-enriched/test_ensure_directory_exists")

    # - Run mkdir_safe

    client.ensure_directory_exists(str(remote_dir / "a/b/c/"))

    # - Check if exists

    assert client.exists(str(remote_dir / "a/b/c/"))

    # - Remove

    client.remove(str(remote_dir), permanently=True)


if __name__ == "__main__":
    pytest.main([__file__])
