TEMPLATE = """#{parent_channel_name}
{emoji} **{title}** by {author}
{body}{tags}
[→ к посту]({url}){apple_link}"""


def format_message(
    parent_channel_name: str,
    emoji: str,
    title: str,
    tags: list[str],
    author_name: str,
    body: str,
    url: str,
    inner_shortened_url: str = "",
    author_url: str = "",
):
    return TEMPLATE.format(
        parent_channel_name=parent_channel_name.replace("-", "_"),
        emoji=emoji,
        title=title,
        author=author_name if not author_url else f"[{author_name}]({author_url})",
        body="\n" + body + "\n" if body else "",
        tags="\n" + " ".join([f"#{tag}" for tag in tags]) + "\n" if tags else "",
        url=url,
        apple_link=f" / [→ к посту для mac]({inner_shortened_url})" if inner_shortened_url else "",
    )


def test():
    print(
        format_message(
            parent_channel_name="<parent_channel_name>",
            emoji="<emoji>",
            title="<title>",
            author_name="<author_name>",
            body="<body>",
            url="<url>",
            inner_shortened_url="<inner_shortened_url>",
        )
    )


if __name__ == "__main__":
    test()
