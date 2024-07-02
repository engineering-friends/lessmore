import asyncio

from learn_language_magic.deps import Deps
from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from learn_language_magic.update_words.extract_words import extract_words
from learn_language_magic.update_words.word import Word
from loguru import logger
from more_itertools import first


async def update_words(word_groups: dict, notion_page_id: str):
    # - Init notion client

    client = NotionRateLimitedClient(auth=Deps.load().config.notion_token)

    # - Get current notion page words

    pages = await client.get_paginated_request(
        method=client.databases.query,
        database_id=notion_page_id,  # words
    )  # [{"archived":false,"cover":null,"created_by":{"id":"bdb47407-ca48-4745-9aff-74763ad1bae0","object":"user"},"created_time":"2024-07-02T16:09:00.000Z","icon":null,"id":"bf276664-4098-4a54-bfd7-31fed6145134","in_trash":false,"last_edited_by":{"id":"bdb47407-ca48-4745-9aff-74763ad1bae0","object":"user"},"last_edited_time":"2024-07-02T17:14:00.000Z","object":"page","parent":{"database_id":"d7a47aa3-4d24-48e3-8e1a-62ed7b6c6775","type":"database_id"},"properties":{"Example Sentence":{"id":"f%7D%3B%7C","rich_text":[],"type":"rich_text"},"Gender":{"id":"aKhX","select":null,"type":"select"},"Group":{"id":"x%7BiC","select":null,"type":"select"},"Irregular Verb":{"checkbox":false,"id":"pXTo","type":"checkbox"},"Notes":{"id":"H%7DHx","rich_text":[],"type":"rich_text"},"Origin":{"id":"oYdr","select":null,"type":"select"},"Part of speech":{"id":"%3DSCD","rich_text":[],"type":"rich_text"},"Plural Form":{"id":"_skw","rich_text":[],"type":"rich_text"},"Pronunciation":{"id":"hA%3F%60","rich_text":[],"type":"rich_text"},"Translation (en)":{"id":"e%3EjT","rich_text":[],"type":"rich_text"},"Translation (ru) ":{"id":"%3BA_Q","rich_text":[],"type":"rich_text"},"Word":{"id":"title","title":[{"annotations":{"bold":false,"code":false,"color":"default","italic":false,"strikethrough":false,"underline":false},"href":null,"plain_text":"Word","text":{"content":"Word","link":null},"type":"text"}],"type":"title"}},"public_url":null,"url":"https://www.notion.so/Word-bf27666440984a54bfd731fed6145134"}, ...]

    logger.info("Fetched current notion word pages", num_pages=len(pages))

    # - Collect words

    words = []
    for word_group_name, word_group in word_groups.items():
        # - Get origin, group and extract words

        if isinstance(word_group, str):
            # - Extract words from stories

            word_groups[word_group_name] = extract_words(word_group)
            continue

        # - Extract words from stories

        _words = word_group if isinstance(word_group, list) else extract_words(word_group)

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
                    for p in pages
                    if first(p["properties"]["word"]["title"], default={}).get("plain_text", "").lower()
                    == word.word.lower()
                ),
                None,
            )

            if page:
                # do not update existing words
                return

            page = await client.pages.create(
                parent={"database_id": notion_page_id},
                properties=await word.build_notion_page_properties(),
            )

            # - Create new blocks

            await client.blocks.children.append(
                block_id=page["id"],
                children=await word.build_notion_page_children(),
            )

        await asyncio.gather(*[_process_word(word) for word in words])


def test():
    async def main():
        print(
            await update_words(
                word_groups={
                    # "story1": "Foo met a Bar",
                    "group_1": ["Laufen", "Hund"],
                },
                notion_page_id="d7a47aa34d2448e38e1a62ed7b6c6775",  # words
            )
        )

    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    test()
