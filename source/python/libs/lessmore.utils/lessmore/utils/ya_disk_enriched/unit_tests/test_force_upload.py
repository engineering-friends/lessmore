import os

from pathlib import Path

import pytest

from lessmore.utils.path_helpers.get_current_dir import get_current_dir


@pytest.mark.slow
def test_force_upload():
    # - Make imports (important to make imports here to avoid circular imports)

    from lessmore.utils.ya_disk_enriched.ya_disk_enriched import YaDiskEnriched

    # - Create client

    client = YaDiskEnriched(token=os.environ["YANDEX_DISK_TOKEN"])

    # - Init test path

    remote_dir = Path("/test-ya-disk-enriched/test_force_upload")

    # - Upload file

    client.force_upload(
        filename=str(get_current_dir() / "test_force_upload.py"),
        remote_filename=str(remote_dir / "test_force_upload.py"),
    )

    # - Check if exists

    assert client.exists(str(remote_dir / "test_force_upload.py"))

    # - Upload file second time

    client.force_upload(
        filename=str(get_current_dir() / "test_force_upload.py"),
        remote_filename=str(remote_dir / "test_force_upload.py"),
    )

    # - Check if exists

    assert client.exists(str(remote_dir / "test_force_upload.py"))

    # - Remove

    client.remove(str(remote_dir), permanently=True)


if __name__ == "__main__":
    test_force_upload()
