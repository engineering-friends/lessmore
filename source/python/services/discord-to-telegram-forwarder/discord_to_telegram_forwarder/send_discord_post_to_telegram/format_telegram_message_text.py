import random

from discord_to_telegram_forwarder.send_discord_post_to_telegram.get_shortened_url_from_tiny_url import (
    get_shortened_url_from_tiny_url,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.request_emoji_from_openai import (
    request_emoji_from_openai,
)
from inline_snapshot import snapshot

from lessmore.utils.backlog.run_inline_snapshot_tests import run_inline_snapshot_tests
from lessmore.utils.easy_printing.print_and_copy import print_and_copy
from lessmore.utils.file_helpers.read_file import read_file
from lessmore.utils.path_helpers.get_current_dir import get_current_dir


def format_telegram_message_text(
    post_author_name: str,
    post_body: str,
    post_forum_channel_name: str,
    post_title: str,
    post_url: str,
    add_inner_shortened_url: bool,
):
    # - Read emoticons

    emoticons = read_file(str(get_current_dir() / "emoticons.txt")).strip().split("\n")

    # - Get emoji from openai

    emoji = request_emoji_from_openai(f"{post_forum_channel_name} {post_title} {post_body}")

    # - Make discord schema and shorten it to make it https:// with redirection to discord://

    inner_shortened_url = (
        get_shortened_url_from_tiny_url(post_url.replace("https", "discord")) if add_inner_shortened_url else ""
    )

    # - Format message for telegram

    text = ""
    if post_forum_channel_name:
        text += f"#{post_forum_channel_name.replace('-', '_')}\n"
    text += f"{emoji} **{post_title}**\n\n"
    if post_body:
        text += (
            post_body[:3000] + ("" if len(post_body) < 3000 else "...") + "\n\n"
        )  # maximum telegram message size is 4096. Making it 3000 to resever space for title and for the buffer
    text += f"{post_author_name} {random.choice(emoticons)}\n"
    text += f"[→ к посту]({post_url})"
    if inner_shortened_url:
        text += f"\n[→ к посту на apple-устройствах]({inner_shortened_url})"
    return text


def test():
    print(
        format_telegram_message_text(
            post_forum_channel_name="channel_name",
            post_title="Тестирую форвардер",
            post_body="",
            post_author_name="Mark Lidenberg",
            post_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
            add_inner_shortened_url=True,
        )
    )

    # example output:
    """#channel_name
🔍 **Тестирую форвардер**

Mark Lidenberg (。◕‿‿◕。)
[→ к посту](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)
[→ к посту на apple-устройствах](https://tinyurl.com/2bub4s6g)"""


if __name__ == "__main__":
    test()
