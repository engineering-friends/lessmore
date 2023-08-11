import os

import yadisk


def test_connection():
    # - Create client

    client = yadisk.YaDisk(token=os.environ["YANDEX_DISK_TOKEN"])

    # - Check if exists

    assert client.exists("/")


if __name__ == "__main__":
    test_connection()
