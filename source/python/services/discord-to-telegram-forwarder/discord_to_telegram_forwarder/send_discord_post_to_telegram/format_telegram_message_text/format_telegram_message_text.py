from typing import Optional

from discord_to_telegram_forwarder.send_discord_post_to_telegram.format_telegram_message_text.get_shortened_url_from_tiny_url import (
    get_shortened_url_from_tiny_url,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.format_telegram_message_text.request_emoji_from_openai import (
    request_emoji_from_openai,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.test_post_kwargs import test_post_kwargs
from inline_snapshot import snapshot

from lessmore.utils.backlog.run_inline_snapshot_tests import run_inline_snapshot_tests


TEMPLATE = """#{channel_name}
{emoji} **"{title}"** by {author}
{body}
[→ к посту]({url}){apple_link}"""


def format_telegram_message_text(
    author_name: str,
    body: str,
    channel_name: str,
    title: str,
    url: str,
    add_inner_shortened_url: bool = True,
    emoji: Optional[str] = None,
):
    # - Get emoji from openai

    if not emoji:
        emoji = request_emoji_from_openai(f"{channel_name} {title} {body}")

    # - Make discord schema and shorten it to make it https:// with redirection to discord://

    inner_shortened_url = (
        get_shortened_url_from_tiny_url(url.replace("https", "discord")) if add_inner_shortened_url else ""
    )

    # - Format message for telegram

    return TEMPLATE.format(
        channel_name=channel_name.replace("-", "_"),
        emoji=emoji,
        title=title,
        author=f"{author_name}",
        body=("\n" + body[:3000] + ("" if len(body) < 3000 else "...")) + "\n" if body else "",
        url=url,
        apple_link=f"\n[→ к посту на apple-устройствах]({inner_shortened_url})" if inner_shortened_url else "",
    )


def test_single():
    print(
        format_telegram_message_text(
            channel_name="channel_name",
            title="Как обходить ограниченный контекст в ChatGPT для больших тасок?",
            body="Вероятно у кого-то из вас уже есть хорошие промпты или тулзы. В частности, хочется научиться батчить - обрабатывать большое количество однотипных джобов",
            author_name="Mark Lidenberg",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
            add_inner_shortened_url=False,
            emoji="📝",
        )
    )


def test_batch():
    assert [format_telegram_message_text(**post_kwargs) for post_kwargs in test_post_kwargs.values()] == snapshot(
        [
            '#channel_name\n💬 **"Basic"** by Mark Lidenberg\n\nThis is my body!\n\n[→ к посту](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)',
            '#channel_name\n📺 **"No body"** by Mark Lidenberg\n\n[→ к посту](https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley)',
        ]
    )


if __name__ == "__main__":
    # test_single()
    run_inline_snapshot_tests()
