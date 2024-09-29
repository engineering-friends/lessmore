import asyncio
import re
import time

from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient


async def parse_telegram_username_by_whois_url(
    text: str,
    notion_client: EnrichedNotionAsyncClient,
    telegram_usernames_by_notion_whois_url: dict = {},  # mutated
    last_checked_telegram_username_at_by_notion_whois_url: dict = {},  # mutated
    logger=None,
) -> str | None:
    # - Parse notion url

    try:
        notion_url = re.findall(r"\[(.*?)\]\((https://www.notion.so/(.*?))\)", text.split("\n")[1])[0][1]
    except:
        return

    notion_url = notion_url.replace("?pvs=4", "")

    if notion_url in telegram_usernames_by_notion_whois_url:
        return telegram_usernames_by_notion_whois_url[notion_url]

    # - Try to get telegram username from notion

    # -- Return if too soon

    if last_checked_telegram_username_at_by_notion_whois_url.get(notion_url, 0) + 3600 > time.time():
        logger.debug("Too soon, try to find telegram username every hour", notion_url=notion_url)

        return

    # - Get pages and update cache

    pages = list(
        await notion_client.get_paginated_request(
            method=notion_client.databases.query,
            method_kwargs=dict(
                database_id="0b1e5db6cdfe4dcea0c818109ce44a26",  # whois_database_id
            ),
        )
    )

    for page in pages:
        telegram_usernames_by_notion_whois_url[page["url"]] = "".join(
            [value["plain_text"] for value in page["properties"]["TG_username"]["rich_text"]]
        )

    # - Update time

    last_checked_telegram_username_at_by_notion_whois_url[notion_url] = time.time()

    # - Check if user is in the database

    return telegram_usernames_by_notion_whois_url.get(notion_url)


async def test():
    from ef_bots.ef_threads.deps import Deps

    async with Deps() as deps:
        assert (
            await parse_telegram_username_by_whois_url(
                text="""🔄 **asdf**'\nby [Mark Lidenberg](https://www.notion.so/Mark-Lidenberg-a09b5c4f599442e1bc7c2201f17214c0)\n\nShould be forwarder\n\n[→ обсудить в дискорде (0)](https://discord.com/channels/1143155301198073956/1247188224862847097/1247188224862847097) | #_test_forum #ai_tools""",
                notion_client=deps.notion_client,
            )
            == "marklidenberg"
        )


if __name__ == "__main__":
    asyncio.run(test())
