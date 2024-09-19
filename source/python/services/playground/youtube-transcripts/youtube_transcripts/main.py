import asyncio
import difflib
import json
import re

from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.file_primitives.read_file import read_file
from lessmore.utils.file_primitives.write_file import write_file
from loguru import logger

from youtube_transcripts.deps import Deps
from youtube_transcripts.get_all_videos_with_transcripts_from_channel.get_all_videos_with_transcripts_from_channel import (
    get_all_videos_with_transcripts_from_channel,
)


def sanitize_filename(filename):
    # Replace any character that is not a letter, number, dot, or underscore with an underscore
    sanitized = re.sub(r"[^\w\.\-]", "_", filename)
    return sanitized


def are_strings_similar(str1, str2, threshold=0.8) -> bool:
    try:
        return difflib.SequenceMatcher(None, str1, str2).ratio() >= threshold
    except:
        logger.error("Failed to compare strings", str1=str1, str2=str2)
        return False


async def main(channel_id: str, notion_token: str, sessions_database_id: str):
    # - Load state

    state = read_file("state.json", reader=json.load, default={})

    # - Get all unprocessed videos from the channel

    videos = get_all_videos_with_transcripts_from_channel(
        exclude_ids=state.get("processed_ids", []),
        channel_id=channel_id,
    )

    # - Find notion page with the same title and add transcripts there

    # -- Init notion client

    client = NotionRateLimitedClient(auth=notion_token)

    # -- Get all pages

    # pages = await client.get_paginated_request(
    #     method=client.databases.query,
    #     method_kwargs=dict(database_id=sessions_database_id),
    # )

    # -- Find page with the same title and add transcripts there

    for video in videos:
        write_file(data=video["caption"], filename=f'transcripts/{sanitize_filename(video["title"])}.txt')

        # page = next(
        #     (
        #         page
        #         for page in pages
        #         if are_strings_similar(page["properties"]["Name"]["title"][0]["text"]["content"], video["title"])
        #     ),
        #     None,
        # )
        # if page:
        #     logger.info("Found page", page_title=page["properties"]["Name"]["title"][0])
        #     await client.pages.update(
        #         page_id=page["id"],
        #         **{"properties": {"transcript": {"rich_text": [{"text": {"content": video["caption"]}}]}}},
        #     )

    # - Update state

    write_file(
        data={"processed_ids": state.get("processed_ids", []) + [video["id"] for video in videos]},
        filename="state.json",
        writer=json.dump,
    )


if __name__ == "__main__":
    asyncio.run(
        main(
            channel_id="UCPx8E004C7cZBZDl7rkBWdA",  # pragma: allowlist secret
            sessions_database_id="1a10179eea4547d9a67f0012d3112127",  # pragma: allowlist secret
            notion_token=Deps.load().config.notion_token,
        )
    )
