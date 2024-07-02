from discord_to_telegram_forwarder.deps import Deps
from discord_to_telegram_forwarder.send_discord_post_to_telegram.ai.ask import ask
from lessmore.utils.cache_on_disk import cache_on_disk
from lessmore.utils.enriched_notion_client import EnrichedNotionClient
from notion_client import Client


PROMPT = """Here is a list of pages. If user {name} if present, return the url of the page. Names can differ a bit, that's ok (but not completely). Otherwise, return "None".

Just the url (like "https://google.com" or "None") 

```{pages}```

"""


def get_whois_url(
    name: str,
    deps: Deps,
    whois_database_id: str = "641eaea7c7ad4881bbed5ea096a4421a",  # ef whois in notion
) -> str:
    # - Init notion client

    client = EnrichedNotionClient(auth=deps.config.notion_token)

    # - Get pages

    pages = list(
        client.get_paginated_request(
            method=client.databases.query,
            database_id=whois_database_id,
        )
    )

    # - Keep only url, filled and title properties

    pages = [
        {
            "url": page["url"],
            "filled": page["properties"]["Filled"]["checkbox"],
            "title": "".join([text["plain_text"] for text in page["properties"]["Name"]["title"]]),
        }
        for page in pages
    ]

    # - Filter filled pages

    pages = [page for page in pages if page["filled"]]

    # - Ask gpt the link for the page with the name

    url = cache_on_disk(directory=f"{deps.local_files_dir}/whois")(ask)(PROMPT.format(name=name, pages=str(pages)))

    if url == "None":
        return None

    return url


def test():
    deps = Deps.load()
    print(get_whois_url("Misha Vodolagin", deps=deps))
    print(get_whois_url("Mark Vodolagin", deps=deps))


if __name__ == "__main__":
    test()
