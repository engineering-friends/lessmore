import asyncio
import json

from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from lessmore.utils.file_primitives.read_file import read_file
from lessmore.utils.file_primitives.write_file import write_file

from youtube_transcripts.get_all_videos_with_transcripts_from_channel import (
    get_all_videos_with_transcripts_from_channel,
)


async def main(channel_id: str, notion_token: str, sessions_database_id: str):
    # - Load state

    state = read_file("state.json", reader=json.load, default={})

    # - Get all unprocessed videos from the channel

    videos = get_all_videos_with_transcripts_from_channel(
        exclude_ids=state.get("processed_ids", []),
        channel_id=channel_id,
    )[-1:]

    # - Find notion page with the same title and add transcripts there

    # -- Init notion client

    client = NotionRateLimitedClient(auth=notion_token)

    # -- Get all pages

    pages = await client.get_paginated_request(
        method=client.databases.query,
        method_kwargs=dict(database_id=sessions_database_id),
    )

    # -- Find page with the same title and add transcripts there

    for video in videos:
        page = next((page for page in pages if page["properties"]["Name"]["title"][0] == video["title"]), None)
        if page:
            page["properties"]["transcript"]["rich_text"] = video["caption"]
            await client.pages.update(page_id=page["id"], **page)

    # - Update state

    # write_file(data=state, filename="state.json", writer=json.dump)


if __name__ == "__main__":
    asyncio.run(main())
