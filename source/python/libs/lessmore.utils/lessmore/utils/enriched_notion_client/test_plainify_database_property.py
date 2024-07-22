import json
import os

from lessmore.utils.file_primitives.local_path.local_path import local_path
from lessmore.utils.file_primitives.read_file import read_file


def test_plainify_database_property():
    from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient

    # - Load page

    page = read_file(
        local_path("data_samples/sample_database_page.json"),
        reader=json.load,
    )

    # - Print page

    for property_name, property in page["properties"].items():
        print(property_name, EnrichedNotionAsyncClient.plainify_database_property(property))


if __name__ == "__main__":
    test_plainify_database_property()
