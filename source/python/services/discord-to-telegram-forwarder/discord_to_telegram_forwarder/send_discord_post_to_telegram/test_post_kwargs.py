test_post_kwargs = {
    "basic": dict(
        channel_name="channel_name",
        title="Basic",
        body="This is my body!",
        author_name="Mark Lidenberg",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
        emoji="💬",
    ),
    "no_body": dict(
        channel_name="channel_name",
        title="No body",
        body="",
        author_name="Mark Lidenberg",
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstley",
        add_inner_shortened_url=False,
        emoji="📺",
    ),
}
