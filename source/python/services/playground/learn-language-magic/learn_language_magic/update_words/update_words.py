import asyncio
import os

from itertools import groupby

from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from learn_language_magic.notion_rate_limited_client import NotionRateLimitedClient
from learn_language_magic.update_words.flatten_word_collection import flatten_word_collection
from learn_language_magic.update_words.upsert_anki_deck import upsert_anki_deck
from learn_language_magic.update_words.word import Word
from learn_language_magic.update_words.word_collection import word_collection
from lessmore.utils.asynchronous.async_cached_property import prefetch_all_cached_properties
from lessmore.utils.functional.skip_duplicates import skip_duplicates
from loguru import logger
from more_itertools import bucket, first


async def update_words(
    word_collection: dict,
    words_database_id: str,
    remove_others: bool = False,
):
    # - Init notion client

    client = NotionRateLimitedClient(auth=Deps.load().config.notion_token)

    # - Flatten word collection

    word_collection = flatten_word_collection(word_collection)

    # - Collect words

    words = []
    for group_name, word_or_bundles in word_collection.items():
        for word_or_bundle in word_or_bundles:
            # - Get bundle name

            bundle_name = None
            if "; " in word_or_bundle or ": " in word_or_bundle:
                if ": " in word_or_bundle:
                    bundle_name = word_or_bundle.split(": ")[0]
                else:
                    bundle_name = await ask(
                        f"Give me a one/two word group name for german words '{word_or_bundle}'. The group_name should be in English",
                        example="Sleep Cycle",
                    )
                    # bundle_name = word_or_bundle

            # - Remove bundle prefix

            if bundle_name:
                word_or_bundle = word_or_bundle.removeprefix(f"{bundle_name}: ")

            # - Split words by ';'

            _words = word_or_bundle.split("; ")

            # - Process words

            for _word in _words:
                # - Split manual translation

                _word, _manual_translation = _word.split("::") if "::" in _word else (_word, "")

                # - Convert to dataclass

                words.append(
                    Word(
                        word=_word,
                        groups=[group_name],
                        bundles=[bundle_name] if bundle_name else [],
                        manual_translation=_manual_translation,
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

    # - Prefetch all properties

    await asyncio.gather(*([prefetch_all_cached_properties(word) for word in words]))

    # - Update notion pages

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

    # await _update_pages()

    # - Update anki deck

    all_group_names = skip_duplicates(sum([word.groups for word in words], []))

    for group_name in all_group_names:
        group_words = [word for word in words if group_name in word.groups]

        logger.info("Upserting anki deck", group_name=group_name, n_words=len(group_words))

        upsert_anki_deck(
            words=[
                {
                    "front": await word.original + ""
                    if not await word.plural
                    else f"{await word.original} ({await word.plural})",
                    "back": f"{await word.emoji} {await word.translation}",
                    "pronunciation": await word.pronunciation,
                    "tags": word.bundles,
                    "plural": await word.plural,
                }
                for word in group_words
            ],
            deck_name=f"Default::{group_name}",
            remove_others=remove_others,
            allow_duplicates="words::" not in group_name,
        )


# fmt: off

def test():
    async def main():
        await update_words(
            # word_collection=word_collection,
            word_collection={'test': {'bundle': ['Minute', 'wordder Tisch; Kapitel']}},
            remove_others=False,
            words_database_id="d7a47aa34d2448e38e1a62ed7b6c6775",  # words
        )

    import asyncio

    asyncio.run(main())


# fmt: on

if __name__ == "__main__":
    test()
