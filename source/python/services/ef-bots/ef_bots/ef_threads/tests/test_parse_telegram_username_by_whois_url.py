import asyncio

from ef_bots.ef_threads.ef_threads import EfThreads


async def test_parse_telegram_username_by_whois_url():
    async with EfThreads().stack() as ef_threads:
        assert (
            await ef_threads.parse_telegram_username_by_whois_url(
                text="""🔄 **asdf**'\nby [Mark Lidenberg](https://www.notion.so/Mark-Lidenberg-a09b5c4f599442e1bc7c2201f17214c0)\n\nShould be forwarder\n\n[→ обсудить в дискорде (0)](https://discord.com/channels/1143155301198073956/1247188224862847097/1247188224862847097) | #_test_forum #ai_tools"""
            )
            == "marklidenberg"
        )


if __name__ == "__main__":
    asyncio.run(test_parse_telegram_username_by_whois_url())
