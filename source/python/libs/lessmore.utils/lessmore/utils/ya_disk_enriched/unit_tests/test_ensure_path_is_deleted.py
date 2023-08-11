import os

from pathlib import Path

import pytest

from lessmore.utils.path_helpers.get_current_dir import get_current_dir


@pytest.mark.slow
def test_ensure_path_is_deleted():
    # - Make imports (important to make imports here to avoid circular imports)

    from lessmore.utils.ya_disk_enriched.ya_disk_enriched import YaDiskEnriched

    # - Init test path

    remote_dir = Path("/test-ya-disk-enriched/test_ensure_path_is_deleted")

    # - Create client

    client = YaDiskEnriched(token=os.environ["YANDEX_DISK_TOKEN"])

    # - Upload file

    client.force_upload(
        filename=str(get_current_dir() / "test_force_upload.py"),
        remote_filename=str(remote_dir / "test_upload_safe.py"),
    )

    # - Check if exists

    assert client.exists(str(remote_dir / "test_upload_safe.py"))

    # - Remove

    client.ensure_path_is_deleted(str(remote_dir))

    # - Check if not exists

    assert not client.exists(str(remote_dir))


if __name__ == "__main__":
    test_ensure_path_is_deleted()
