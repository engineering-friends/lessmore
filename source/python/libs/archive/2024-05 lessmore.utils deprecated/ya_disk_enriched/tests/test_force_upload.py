import os

from pathlib import Path

import pytest

from lessmore.utils.ya_disk_enriched.tests.init_test_client import init_client


@pytest.mark.slow
def test_force_upload():
    # - Init client

    client = init_client()

    # - Init test path

    remote_dir = Path("/test-ya-disk-enriched/test_force_upload")

    # - Upload file

    client.force_upload(
        filename=str(Path(__file__).parent / "test_force_upload.py"),
        remote_filename=str(remote_dir / "test_force_upload.py"),
    )

    # - Check if exists

    assert client.exists(str(remote_dir / "test_force_upload.py"))

    # - Upload file second time

    client.force_upload(
        filename=str(Path(__file__).parent / "test_force_upload.py"),
        remote_filename=str(remote_dir / "test_force_upload.py"),
    )

    # - Check if exists

    assert client.exists(str(remote_dir / "test_force_upload.py"))

    # - Remove

    client.remove(str(remote_dir), permanently=True)


if __name__ == "__main__":
    pytest.main([__file__])
