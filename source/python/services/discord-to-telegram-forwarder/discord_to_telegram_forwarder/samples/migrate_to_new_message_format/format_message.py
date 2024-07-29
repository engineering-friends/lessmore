import asyncio
import json
import re

from pathlib import Path

import keyring

from discord_to_telegram_forwarder.deps import Deps
from more_itertools import first
from telethon import TelegramClient


BEFORE_EXAMPLE = """#_test_forum
🔄 **asdf** by [Mark Lidenberg](https://www.notion.so/Mark-Lidenberg-d5ae5f192b4c402ba014268e63aed47c)

Should be forwarder

#ai_tools

[→ к посту](https://discord.com/channels/1143155301198073956/1247188224862847097/1247188224862847097) / [→ к посту для mac](https://tinyurl.com/29np99cy) (0)"""

AFTER_EXAMPLE = """🔄 **asdf**
by [Mark Lidenberg](https://www.notion.so/Mark-Lidenberg-d5ae5f192b4c402ba014268e63aed47c)

Should be forwarder

[→ обсудить в дискорде](https://discord.com/channels/1143155301198073956/1247188224862847097/1247188224862847097) (0) | #_test_forum #ai_tools
"""


def format_message(text: str) -> str:
    # - Parse к посту

    links = re.findall(r"\[→ к посту.*?\]\((.*?)\)", text)
    discussion_link = links[0] if links else ""

    # - Change footer

    if discussion_link:
        # - Find comments counter (123) -> 123

        counters = re.findall(r"\(\+(\d+)\)", text)

        if not counters:
            counters = [0]

        counter = counters[-1]
        counter = int(counter)

        # - Find tags

        tags = re.findall(r"#[\w-]+", text)
        tag_text = " ".join(tags).replace("-", "_")
        tag_text = tag_text.replace("#general", "#posts")

        # - Replace tags with ''

        for tag in tags:
            text = text.replace(tag, "")

        text = re.sub(r"\[→ к посту.*?\]\(.*?\).+$", "", text)

        if discussion_link:
            counter_string = "" if counter == 0 else f" (+{counter})"
            text += f"[→ обсудить в дискорде{counter_string}]({discussion_link}) | {tag_text}"

    # - Change title

    by_author = ""

    for line in text.split("\n")[:2]:
        if line[:2] == "by":
            continue

        if "by" in line:
            by_author = first(re.findall(r"( by .+)$", line), default="")
            break

    if by_author:
        text = text.replace(by_author, "\n" + by_author[1:])

    # - Remove two new lines

    text = re.sub(r"\n\n\n*", "\n\n", text)

    # - Remove empty lines at the start

    text = re.sub(r"^\n+", "", text)

    return text


if __name__ == "__main__":
    print(
        format_message("""#_test_forum
🔄 **asdf** by [Mark Lidenberg](https://www.notion.so/Mark-Lidenberg-d5ae5f192b4c402ba014268e63aed47c)

Should be forwarder

#ai-tools

[→ к посту](https://discord.com/channels/1143155301198073956/1247188224862847097/1247188224862847097) / [→ к посту для mac](https://tinyurl.com/29np99cy) (+10)
""")
    )
