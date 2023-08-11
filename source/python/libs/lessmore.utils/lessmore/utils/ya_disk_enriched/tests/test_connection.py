import pytest

from lessmore.utils.ya_disk_enriched.tests.client import client  # pytest fixture


def test_connection(client):
    # - Check if exists

    assert client.exists("/")


if __name__ == "__main__":
    pytest.main([__file__])
