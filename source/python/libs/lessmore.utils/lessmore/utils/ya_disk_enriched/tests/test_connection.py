import pytest

from lessmore.utils.ya_disk_enriched.tests.init_test_client import init_client


def test_connection():
    # - Init client

    client = init_client()

    # - Check if exists

    assert client.exists("/")


if __name__ == "__main__":
    pytest.main([__file__])
