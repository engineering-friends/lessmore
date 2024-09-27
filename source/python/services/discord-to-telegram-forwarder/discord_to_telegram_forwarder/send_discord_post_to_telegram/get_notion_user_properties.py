from lessmore.utils.cache_on_disk import cache_on_disk
from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient
from lessmore.utils.functional.dict.pick import pick
from more_itertools import first

from discord_to_telegram_forwarder.deps import Deps
from discord_to_telegram_forwarder.send_discord_post_to_telegram.ai.ask import ask


PROMPT = """Here is a list of pages. If user {name} if present, return the url of the page. Names can differ a bit, that's ok (but not completely). Otherwise, return "None".

Just the url (like "https://google.com" or "None") 

```{pages}```

"""


PROPERTY_NAMES = ["Name", "TG_username", "AI стиль постов", "Заполнена"]


async def get_notion_user_properties(
    name: str,
    deps: Deps,
    whois_database_id: str = "0b1e5db6cdfe4dcea0c818109ce44a26",  # ef whois in notion
) -> dict:
    # - Init notion client

    client = EnrichedNotionAsyncClient(auth=deps.config.notion_token)

    # - Get pages from the whois page

    pages = list(
        await client.get_paginated_request(
            method=client.databases.query,
            method_kwargs=dict(
                database_id=whois_database_id,
            ),
        )
    )

    # - Drop non-supported properties (relations, formulas, people)

    pages = [
        {
            **pick(
                {
                    property_name: client.plainify_database_property(property=property)
                    for property_name, property in page["properties"].items()
                    if property
                    and property["type"] not in ["relation", "formula", "people"]  # filter out unsupported properties
                },
                keys=PROPERTY_NAMES,
            ),
            **{"url": page["url"]},
        }
        for page in pages
    ]

    assert all(property_name in pages[0] for property_name in PROPERTY_NAMES)

    # - Ask gpt the link for the page with the name

    url = cache_on_disk(directory=f"{deps.local_files_dir}/whois")(ask)(PROMPT.format(name=name, pages=str(pages)))

    if url == "None":
        return {}
    else:
        return first([page for page in pages if page["url"] == url], default={})


def test():
    async def main():
        deps = Deps.load()
        print(await get_notion_user_properties("Misha Vodolagin", deps=deps))
        print(await get_notion_user_properties("Mark Vodolagin", deps=deps))

    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    test()
