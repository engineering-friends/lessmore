import pandas as pd

from learn_language_magic.update_vocabulary.upsert_anki_deck import upsert_anki_deck
from lessmore.utils.functional.skip_duplicates import skip_duplicates
from loguru import logger


async def update_vocabulary(vocabulary_database_id: str):
    # - Load words

    from learn_language_magic.deps import Deps

    deps = Deps.load()

    from lessmore.utils.enriched_notion_client.enriched_notion_async_client import EnrichedNotionAsyncClient

    client = EnrichedNotionAsyncClient(auth=deps.config.notion_token)

    pages = await client.get_paginated_request(
        method=client.databases.query, method_kwargs={"database_id": vocabulary_database_id}
    )
    properties_list = [page["properties"] for page in pages]
    properties_list = [
        {k: client.plainify_database_property(v) for k, v in properties.items()} for properties in properties_list
    ]

    df = pd.DataFrame(properties_list)

    # - Update anki deck

    for deck, grp in df.groupby("deck"):
        upsert_anki_deck(
            words=[
                {
                    "front": row["name"] + "" if not await row["plural"] else f"{row['name']} ({row['plural']})",
                    "back": f"{row['emoji']} {await row['translation']}",
                    "pronunciation": row["pronunciation"],
                }
                for i, row in grp.iterrows()
            ],
            deck_name=f"Default::{deck}",
            remove_others=False,
            allow_duplicates="words::" not in deck,
        )


# fmt: off

def test():
    async def main():
        await update_vocabulary(
            vocabulary_database_id="1f38a3aab8c14da19bb1b4317bdbc148"
        )

    import asyncio

    asyncio.run(main())


# fmt: on

if __name__ == "__main__":
    test()
