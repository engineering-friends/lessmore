import asyncio
import json
import re
import textwrap

from dataclasses import dataclass

from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from lessmore.utils.asynchronous.async_cached_property import async_cached_property, prefetch_all_cached_properties
from more_itertools import mark_ends


@dataclass
class Word:
    word: str
    groups: list[str]
    bundles: list[str]

    @async_cached_property
    async def translation(self):
        return await ask(
            f"""Add english translation for the german word '{self.word}'. Keep it as brief as possible""",
            example="🐶",
        )

    @async_cached_property
    async def emoji(self):
        emoji = await ask(
            f"""Add emoji for the german word '{self.word}'""",
            example="🐶",
        )

        if (
            await ask(
                # f"""Would emoji {emoji} be suitable for the german word '{self.word}' in the dictionary? (yes/no)""",
                f"""Is emoji {emoji} is a good illustration for the german word '{self.word}'? (yes/no)""",
                example="yes",
            )
            == "yes"
        ):
            return emoji
        else:
            return "💬"

    @async_cached_property
    async def pronunciation(self):
        return await ask(
            f"""Add pronunciation for the german word '{self.word}'""",
            example="dɛr hʊnt",
        )

    @async_cached_property
    async def notion_page(self):
        # - Build properties

        result = {
            "properties": {
                "word": {"title": [{"text": {"content": self.word}}]},
                "groups": {"multi_select": [{"name": group} for group in self.groups]},
                "bundles": {"multi_select": [{"name": bundle} for bundle in self.bundles]},
                "translation": {"rich_text": [{"text": {"content": await self.translation}}]},
                "emoji": {"rich_text": [{"text": {"content": await self.emoji}}]},
                "pronunciation": {"rich_text": [{"text": {"content": await self.pronunciation}}]},
            },
            "children": [],  # not using children for now
        }

        # - Filter out None values

        return {k: v for k, v in result.items() if v is not None}


def test():
    async def main():
        Deps.load()
        word = Word(
            word="hunds",
            groups=["test_group"],
            bundles=["test_bundle"],
        )
        print(
            json.dumps(
                await asyncio.gather(*[prefetch_all_cached_properties(word), word.notion_page]),
                indent=2,
                ensure_ascii=False,
            )
        )

    asyncio.run(main())


if __name__ == "__main__":
    test()
