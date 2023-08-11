import os


def test_force_upload():

    # - Make imports (important to make imports here to avoid circular imports)

    from lessmore.utils.ya_disk_enriched.ya_disk_enriched import YaDiskEnriched

    # - Create client

    client = YaDiskEnriched(token=os.environ["YANDEX_DISK_TOKEN"])

    # - Upload file

    client.force_upload(
        filename="test_force_upload.py",
        remote_filename="/test-ya-disk-enriched/test_upload_safe.py",
    )

    # - Check if exists

    assert client.exists("/test-ya-disk-enriched/test_upload_safe.py")

    # - Upload file second time

    client.force_upload(
        filename="test_force_upload.py",
        remote_filename="/test-ya-disk-enriched/test_upload_safe.py",
    )

    # - Check if exists

    assert client.exists("/test-ya-disk-enriched/test_upload_safe.py")

    # - Remove

    client.remove("/test-ya-disk-enriched", permanently=True)


if __name__ == "__main__":
    test_force_upload()
