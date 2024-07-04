import asyncio
import os

from itertools import groupby

from learn_language_magic.deps import Deps
from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from learn_language_magic.update_words.extract_words import extract_words
from learn_language_magic.update_words.word import Word
from learn_language_magic.update_words.word_groups import word_groups
from lessmore.utils.asynchronous.async_cached_property import prefetch_all_cached_properties
from lessmore.utils.functional.skip_duplicates import skip_duplicates
from loguru import logger
from more_itertools import bucket, first


async def update_words(
    word_groups: dict,
    words_database_id: str,
    stories_database_id: str,
    update_page_contents: bool = False,
):
    # - Init notion client

    client = NotionRateLimitedClient(auth=Deps.load().config.notion_token)

    # - Collect words

    words = []
    for word_group_name, word_group in word_groups.items():
        # - Extract words from stories

        _words = word_group if isinstance(word_group, list) else await extract_words(word_group)

        # - Add story to stories database if needed

        if isinstance(word_group, str):
            await client.upsert_database(
                database={"id": stories_database_id},
                pages=[
                    {
                        "properties": {"Name": {"title": [{"text": {"content": word_group_name}}]}},
                        "children": [
                            {
                                "type": "paragraph",
                                "paragraph": {"rich_text": [{"text": {"content": word_group}}]},
                            }
                        ],
                    }
                ],
                page_unique_id_func=lambda page: page["properties"]["Name"]["title"][0]["text"]["content"],
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
                    groups=[word_group_name] if isinstance(word_group, list) else None,
                )
            )

    # - Merge words with same word

    _words = []

    for key, same_words in groupby(
        sorted(words, key=lambda word: word.word.lower()), key=lambda word: word.word.lower()
    ):
        # - Unpack iterator

        same_words = list(same_words)

        # - Get sample word - it will be used to merge the group

        _word = same_words[0]

        # - Update word

        _word.groups = list(skip_duplicates([word.groups[0] for word in same_words if word.groups]))

        # - Add to new words

        _words.append(_word)
    words = _words

    logger.info("Collected words", n_words=len(words))

    # - Remove images for pages where `refresh_image` set to True

    # -- Get all words pages

    word_pages = await client.get_paginated_request(
        method=client.databases.query,
        database_id=words_database_id,
    )

    # -- Select word pages that need refreshing

    refreshed_pages = [page for page in word_pages if page["properties"]["refresh_image"]["checkbox"]]

    refreshed_titles = [first(page["properties"]["word"]["title"])["text"]["content"] for page in refreshed_pages]

    # -- Remove images for pages that need refreshing

    for page in refreshed_pages:
        word_title = first(page["properties"]["word"]["title"])["text"]["content"]
        filename = os.path.join(os.path.dirname(__file__), f"../data/dynamic/images/{word_title}.png")
        if os.path.exists(filename):
            os.remove(filename)

    # - Process words

    async def _update_pages():
        # - Get all words pages

        word_pages = await asyncio.gather(*[word.notion_page for word in words])

        # - Remove children if not updated

        for page in word_pages:
            if not (
                update_page_contents
                or first(page["properties"]["word"]["title"])["text"]["content"] in refreshed_titles
                or not page.get("id")
            ):
                # no need to update
                page["children"] = None

        # - Update pages

        await client.upsert_database(
            database={"id": words_database_id},
            pages=word_pages,
            page_unique_id_func=lambda page: page["properties"]["word"]["title"][0]["text"]["content"],
        )

    await asyncio.gather(*([prefetch_all_cached_properties(word) for word in words] + [_update_pages()]))


# fmt: off

def test():
    async def main():
        print(
            await update_words(
                word_groups=word_groups,
                # word_groups={'test': ['laufen']},
                words_database_id="d7a47aa34d2448e38e1a62ed7b6c6775",  # words
                stories_database_id="8d9d6643302c48649345209e18dbb0ca",  # stories
                update_page_contents=False
            )
        )
        

    import asyncio

    asyncio.run(main())

# fmt: on

if __name__ == "__main__":
    test()
