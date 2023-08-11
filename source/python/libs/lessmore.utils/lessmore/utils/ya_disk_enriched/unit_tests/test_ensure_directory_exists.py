import os


def test_ensure_directory_exists():

    # - Make imports (important to make imports here to avoid circular imports)

    from lessmore.utils.ya_disk_enriched.ya_disk_enriched import YaDiskEnriched

    # - Create client

    client = YaDiskEnriched(token=os.environ["YANDEX_DISK_TOKEN"])

    # - Run mkdir_safe

    client.ensure_directory_exists("/test-ya-disk-enriched/a/b/c/")

    # - Check if exists

    assert client.exists("/test-ya-disk-enriched/a/b/c/")

    # - Remove

    client.remove("/test-ya-disk-enriched", permanently=True)


if __name__ == "__main__":
    test_ensure_directory_exists()
