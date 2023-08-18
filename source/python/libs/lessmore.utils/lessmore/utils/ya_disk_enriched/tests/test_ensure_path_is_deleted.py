import os

from pathlib import Path

import keyring
import pytest

from lessmore.utils.path_helpers.get_current_dir import get_current_dir
from lessmore.utils.ya_disk_enriched.tests.init_test_client import init_client


@pytest.mark.slow
def test_ensure_path_is_deleted():
    # - Init client

    client = init_client()

    # - Init test path

    remote_dir = Path("/test-ya-disk-enriched/test_ensure_path_is_deleted")

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
    pytest.main([__file__])
