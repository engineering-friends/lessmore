import random

from typing import Optional

from discord_to_telegram_forwarder.send_discord_post_to_telegram.get_shortened_url_from_tiny_url import (
    get_shortened_url_from_tiny_url,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.request_emoji_from_openai import (
    request_emoji_from_openai,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.tests.messages import test_messages
from inline_snapshot import snapshot

from lessmore.utils.backlog.run_inline_snapshot_tests import run_inline_snapshot_tests


TEMPLATE = """#{channel_name}
{emoji} **"{title}"** by {author}
{body}
[→ к посту]({url}){apple_link}"""


def format_telegram_message_text(
    post_author_name: str,
    post_body: str,
    post_forum_channel_name: str,
    post_title: str,
    post_url: str,
    add_inner_shortened_url: bool,
    emoji: Optional[str] = None,
):
    # - Get emoji from openai

    if not emoji:
        emoji = request_emoji_from_openai(f"{post_forum_channel_name} {post_title} {post_body}")

    # - Make discord schema and shorten it to make it https:// with redirection to discord://

    inner_shortened_url = (
        get_shortened_url_from_tiny_url(post_url.replace("https", "discord")) if add_inner_shortened_url else ""
    )

    # - Format message for telegram

    return TEMPLATE.format(
        channel_name=post_forum_channel_name.replace("-", "_"),
        emoji=emoji,
        title=post_title,
        author=f"{post_author_name}",
        body=("\n" + post_body[:3000] + ("" if len(post_body) < 3000 else "...")) + "\n" if post_body else "",
        url=post_url,
        apple_link=f"\n[→ к посту на apple-устройствах]({inner_shortened_url})" if inner_shortened_url else "",
    )


def test_single():
    print(
        format_telegram_message_text(
            post_forum_channel_name="channel_name",
            post_title="Как обходить ограниченный контекст в ChatGPT для больших тасок?",
            post_body="Вероятно у кого-то из вас уже есть хорошие промпты или тулзы. В частности, хочется научиться батчить - обрабатывать большое количество однотипных джобов",
            post_author_name="Mark Lidenberg",
            post_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
            add_inner_shortened_url=False,
            emoji="📝",
        )
    )


def test_batch():
    assert [format_telegram_message_text(**message) for message in test_messages.values()] == snapshot(
        [
            '#channel_name\n💬 **"Basic"** by Mark Lidenberg\n\nThis is my body!\n\n[→ к посту](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)\n[→ к посту на apple-устройствах](https://tinyurl.com/2bub4s6g)',
            '#channel_name\n📺 **"No body"** by Mark Lidenberg\n\n\n[→ к посту](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)\n[→ к посту на apple-устройствах](https://tinyurl.com/2bub4s6g)',
        ]
    )


if __name__ == "__main__":
    # test_single()
    run_inline_snapshot_tests()
