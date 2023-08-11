import os

from pathlib import Path

import pytest

from lessmore.utils.ya_disk_enriched.tests.client import client  # pytest fixture


@pytest.mark.slow
def test_ensure_directory_exists(client):
    # - Make imports (important to make imports here to avoid circular imports)

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
