import asyncio

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
                database_id=stories_database_id,
                pages=[
                    {
                        "parent": {"database_id": stories_database_id},
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
        # - Get sample word - it will be used to merge the group

        _word = next(same_words)

        # - Update word

        _word.groups = list(skip_duplicates([word.groups[0] for word in same_words if word.groups]))

        # - Add to new words

        _words.append(_word)
    words = _words

    # - Process words

    await asyncio.gather(
        *(
            [prefetch_all_cached_properties(word) for word in words]
            + [client.upsert_database(database_id=words_database_id, pages=[await word.notion_page]) for word in words]
        )
    )


# fmt: off

def test():
    async def main():
        print(
            await update_words(
                word_groups=word_groups,
                # word_groups={'test': 'laufen'},
                words_database_id="d7a47aa34d2448e38e1a62ed7b6c6775",  # words
                stories_database_id="8d9d6643302c48649345209e18dbb0ca",  # stories
                force_update=True
            )
        )
        
# fmt: on

    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    test()
