import asyncio
import re

from ef_bots.ef_threads.deps.deps import Deps
from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient


async def parse_telegram_username_by_whois_url(
    text: str,
    notion_client: EnrichedNotionAsyncClient,
    cache: dict = {},
) -> dict:
    # - Parse notion url

    try:
        notion_url = re.findall(r"\[(.*?)\]\((https://www.notion.so/(.*?))\)", text.split("\n")[1])[0][1]
    except:
        return

    notion_url = notion_url.replace("?pvs=4", "")

    if notion_url not in cache:
        pages = list(
            await notion_client.get_paginated_request(
                method=notion_client.databases.query,
                method_kwargs=dict(
                    database_id="0b1e5db6cdfe4dcea0c818109ce44a26",  # whois_database_id
                ),
            )
        )

    for page in pages:
        cache[page["url"]] = "".join([value["plain_text"] for value in page["properties"]["TG_username"]["rich_text"]])

    # - Check if user is in the database

    return cache.get(notion_url)


def test():
    async def main():
        # - Init deps

        deps = Deps.load()

        text = """🔄 **asdf**'\nby [Mark Lidenberg](https://www.notion.so/Mark-Lidenberg-a09b5c4f599442e1bc7c2201f17214c0)\n\nShould be forwarder\n\n[→ обсудить в дискорде (0)](https://discord.com/channels/1143155301198073956/1247188224862847097/1247188224862847097) | #_test_forum #ai_tools"""
        print(await parse_telegram_username_by_whois_url(text, notion_client=deps.notion_client()))

    asyncio.run(main())


if __name__ == "__main__":
    test()
