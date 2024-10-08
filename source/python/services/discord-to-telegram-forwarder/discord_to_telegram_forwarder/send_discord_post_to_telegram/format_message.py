from inline_snapshot import snapshot
from lessmore.utils.run_snapshot_tests.run_shapshot_tests import run_snapshot_tests


TEMPLATE = """{emoji} **{title}** 
by {author}
{body}
[→ обсудить в дискорде]({url}) | #{parent_channel_name} {tags}"""

TEMPLATE_NO_DISCORD_LINKS = """{emoji} **{title}** 
by {author}
{body}
#{parent_channel_name} {tags}"""


def format_message(
    parent_channel_name: str,
    emoji: str,
    title: str,
    tags: list[str],
    author_name: str,
    body: str,
    url: str,
    author_url: str = "",
    inner_shortened_url: str = "",  # deprecated
    disable_discord_links: bool = False,
):
    if not disable_discord_links:
        return TEMPLATE.format(
            parent_channel_name=parent_channel_name.replace("-", "_"),
            emoji=emoji,
            title=title,
            author=author_name if not author_url else f"[{author_name}]({author_url})",
            body="\n" + body + "\n" if body else "",
            tags=" ".join([f"#{tag}" for tag in tags]) + "\n" if tags else "",
            url=url,
        )
    else:
        return TEMPLATE_NO_DISCORD_LINKS.format(
            parent_channel_name=parent_channel_name.replace("-", "_"),
            emoji=emoji,
            title=title,
            author=author_name if not author_url else f"[{author_name}]({author_url})",
            body="\n" + body + "\n" if body else "",
            tags=" ".join([f"#{tag}" for tag in tags]) + "\n" if tags else "",
        )


def test():
    assert (
        format_message(
            parent_channel_name="<parent_channel_name>",
            emoji="<emoji>",
            title="<title>",
            author_name="<author_name>",
            body="<body>",
            url="<url>",
            inner_shortened_url="<inner_shortened_url>",
            tags=["want_a_session"],
        )
    ) == snapshot("""\
<emoji> **<title>** 
by <author_name>

<body>

[→ обсудить в дискорде](<url>) | #<parent_channel_name> #want_a_session
""")


if __name__ == "__main__":
    # test()
    run_snapshot_tests(mode="update_all")
