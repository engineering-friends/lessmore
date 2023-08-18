import keyring
import pytest


def init_client():
    from lessmore.utils.ya_disk_enriched.ya_disk_enriched import YaDiskEnriched

    return YaDiskEnriched(
        token=keyring.get_password(
            service_name="yandex-api",
            username="marklidenberg@gmail.com",
        )
    )
