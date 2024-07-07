import asyncio
import os

from itertools import groupby

from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from learn_language_magic.update_words.word import Word
from learn_language_magic.update_words.word_collection import word_collection
from lessmore.utils.asynchronous.async_cached_property import prefetch_all_cached_properties
from lessmore.utils.functional.skip_duplicates import skip_duplicates
from loguru import logger
from more_itertools import bucket, first


async def update_words(
    word_collection: dict,
    words_database_id: str,
):
    # - Init notion client

    client = NotionRateLimitedClient(auth=Deps.load().config.notion_token)

    # - Collect words

    words = []
    for group_name, word_or_bundle in word_collection.items():
        # - Get bundle name

        bundle_name = None
        if ";" in group_name or ":" in group_name:
            if ":" in group_name:
                bundle_name = group_name.split(":")[0]
            else:
                bundle_name = await ask(
                    f"Provide a single one, at most two word name for the group: {bundle_name}", example="Friends"
                )

        # - Split words by ';'

        _words = word_or_bundle.split(";")

        # - Process words

        for _word in _words:
            # - Convert to dataclass

            words.append(
                Word(
                    word=_word,
                    groups=[group_name],
                    bundles=[bundle_name],
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
        _word.bundles = list(skip_duplicates([word.bundles[0] for word in same_words if word.bundles]))

        # - Add to new words

        _words.append(_word)
    words = _words

    logger.info("Collected words", n_words=len(words))

    # - Process words

    async def _update_pages():
        # - Get all words pages

        word_pages = await asyncio.gather(*[word.notion_page for word in words])

        # - Update pages

        await client.upsert_database(
            database={"id": words_database_id},
            pages=word_pages,
            page_unique_id_func=lambda page: page["properties"]["word"]["title"][0]["text"]["content"],
            remove_others=True,
        )

    await asyncio.gather(*([prefetch_all_cached_properties(word) for word in words] + [_update_pages()]))


# fmt: off

def test():
    async def main():
        await update_words(
            word_collection=word_collection,
            # word_groups={'test': ['das Mädchen und das Haus']},
            words_database_id="d7a47aa34d2448e38e1a62ed7b6c6775",  # words
        )

    import asyncio

    asyncio.run(main())


# fmt: on

if __name__ == "__main__":
    test()
