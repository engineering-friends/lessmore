import os

from pathlib import Path

import pytest


@pytest.mark.slow
def test_ensure_directory_exists():
    # - Make imports (important to make imports here to avoid circular imports)

    from lessmore.utils.ya_disk_enriched.ya_disk_enriched import YaDiskEnriched

    # - Init test path

    remote_dir = Path("/test-ya-disk-enriched/test_ensure_directory_exists")

    # - Create client

    client = YaDiskEnriched(token=os.environ["YANDEX_DISK_TOKEN"])

    # - Run mkdir_safe

    client.ensure_directory_exists(str(remote_dir / "a/b/c/"))

    # - Check if exists

    assert client.exists(str(remote_dir / "a/b/c/"))

    # - Remove

    client.remove(str(remote_dir), permanently=True)


if __name__ == "__main__":
    test_ensure_directory_exists()
