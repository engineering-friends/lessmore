import asyncio

from learn_language_magic.deps import Deps
from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from learn_language_magic.update_words.extract_words import extract_words
from learn_language_magic.update_words.word import Word
from lessmore.utils.asynchronous.async_cached_property import prefetch_all_cached_properties
from lessmore.utils.functional.skip_duplicates import skip_duplicates
from loguru import logger
from more_itertools import first


async def update_words(word_groups: dict, words_database_id: str, stories_database_id: str):
    # - Init notion client

    client = NotionRateLimitedClient(auth=Deps.load().config.notion_token)

    # - Get current notion page words

    word_pages = await client.get_paginated_request(
        method=client.databases.query,
        database_id=words_database_id,  # words
    )  # [{"archived":false,"cover":null,"created_by":{"id":"bdb47407-ca48-4745-9aff-74763ad1bae0","object":"user"},"created_time":"2024-07-02T16:09:00.000Z","icon":null,"id":"bf276664-4098-4a54-bfd7-31fed6145134","in_trash":false,"last_edited_by":{"id":"bdb47407-ca48-4745-9aff-74763ad1bae0","object":"user"},"last_edited_time":"2024-07-02T17:14:00.000Z","object":"page","parent":{"database_id":"d7a47aa3-4d24-48e3-8e1a-62ed7b6c6775","type":"database_id"},"properties":{"Example Sentence":{"id":"f%7D%3B%7C","rich_text":[],"type":"rich_text"},"Gender":{"id":"aKhX","select":null,"type":"select"},"Group":{"id":"x%7BiC","select":null,"type":"select"},"Irregular Verb":{"checkbox":false,"id":"pXTo","type":"checkbox"},"Notes":{"id":"H%7DHx","rich_text":[],"type":"rich_text"},"Origin":{"id":"oYdr","select":null,"type":"select"},"Part of speech":{"id":"%3DSCD","rich_text":[],"type":"rich_text"},"Plural Form":{"id":"_skw","rich_text":[],"type":"rich_text"},"Pronunciation":{"id":"hA%3F%60","rich_text":[],"type":"rich_text"},"Translation (en)":{"id":"e%3EjT","rich_text":[],"type":"rich_text"},"Translation (ru) ":{"id":"%3BA_Q","rich_text":[],"type":"rich_text"},"Word":{"id":"title","title":[{"annotations":{"bold":false,"code":false,"color":"default","italic":false,"strikethrough":false,"underline":false},"href":null,"plain_text":"Word","text":{"content":"Word","link":null},"type":"text"}],"type":"title"}},"public_url":null,"url":"https://www.notion.so/Word-bf27666440984a54bfd731fed6145134"}, ...]

    # - Get all stories pages

    story_pages = await client.get_paginated_request(
        method=client.databases.query,
        database_id=stories_database_id,  # stories
    )

    logger.info("Fetched current notion word pages", num_pages=len(word_pages))

    # - Collect words

    words = []
    for word_group_name, word_group in word_groups.items():
        # - Extract words from stories

        _words = word_group if isinstance(word_group, list) else await extract_words(word_group)

        # - Add story to stories database if needed

        if isinstance(word_group, str):
            # - Try to find word in notion pages

            page = next(
                (
                    p
                    for p in story_pages
                    if first(p["properties"]["Name"]["title"], default={}).get("plain_text", "").lower()
                    == word_group_name.lower()
                ),
                None,
            )

            if not page:
                logger.debug("Creating new story page", word_group_name=word_group_name)

                # - Create page

                page = await client.pages.create(
                    parent={"database_id": stories_database_id},
                    properties={
                        "Name": {"title": [{"text": {"content": word_group_name}}]},
                    },
                )

                # - Add paragraph block with text

                await client.blocks.children.append(
                    block_id=page["id"],
                    children=[
                        {
                            "type": "paragraph",
                            "paragraph": {"rich_text": [{"text": {"content": word_group}}]},
                        }
                    ],
                )

        logger.info("Processing group", group=word_group_name, words=_words)

        # - Process words

        for _word in _words:
            # - Convert to dataclass

            words.append(
                Word(
                    word=_word,
                    origin=word_group_name,
                    origin_text=word_group if isinstance(word_group, str) else None,
                    group=word_group_name if isinstance(word_group, list) else None,
                )
            )

    # - Process each word

    async def _process_word(word: Word):
        logger.info("Processing word", word=word.word)

        # - Try to find word in notion pages

        page = next(
            (
                p
                for p in word_pages
                if first(p["properties"]["word"]["title"], default={}).get("plain_text", "").lower()
                == word.word.lower()
            ),
            None,
        )

        if page:
            # do not update existing words
            return

        # - Create new page

        logger.debug("Creating new word page", word=word.word, properties=await word.notion_page_properties)

        page = await client.pages.create(
            parent={"database_id": words_database_id},
            properties=await word.notion_page_properties,
        )

        # - Create new blocks

        await client.blocks.children.append(
            block_id=page["id"],
            children=await word.notion_page_children,
        )

    # - Filter unique words

    words = list(skip_duplicates(words, key=lambda w: w.word.lower()))

    # - Process words

    await asyncio.gather(
        *([prefetch_all_cached_properties(word) for word in words] + [_process_word(word) for word in words])
    )


def test():
    async def main():
        print(
            await update_words(
                word_groups={
                    "story1": "Mr. und Mrs. Dursley im Ligusterweg Nummer 4 waren stolz darauf, ganz und gar normal zu sein, sehr stolz sogar",
                    "group_1": ["Laufen", "Hund"],
                    "group_2": ["Mrs."],
                },
                words_database_id="d7a47aa34d2448e38e1a62ed7b6c6775",  # words
                stories_database_id="8d9d6643302c48649345209e18dbb0ca",  # stories
            )
        )

    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    test()
