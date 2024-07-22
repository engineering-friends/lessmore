import asyncio
import json
import re
import textwrap

from dataclasses import dataclass

from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from learn_language_magic.markdown_table_to_df import markdown_table_to_df
from lessmore.utils.asynchronous.async_cached_property import async_cached_property, prefetch_all_cached_properties
from lessmore.utils.enriched_notion_client.enriched_notion_client import EnrichedNotionAsyncClient
from more_itertools import mark_ends


@dataclass
class Word:
    word: str
    groups: list[str]
    bundles: list[str]
    manual_translation: str = ""

    @async_cached_property
    async def translation(self):
        return self.manual_translation or await ask(
            f"""Add english translation for the german word '{self.word}'""",
            example="🐶",
        )

    @async_cached_property
    async def original(self):
        result = ""

        result += self.word

        if await self.is_irregular_verb:
            df = markdown_table_to_df(await self.irregular_verb_conjugation)

            df = df[df["Irregular"] == "x"]
            df.pop("Irregular")
            # change er/sie/es -> er
            df["Pronoun"] = df["Pronoun"].apply(lambda x: re.sub(r"/.*", "", x))
            values = []
            for i, row in df.iterrows():
                values.append(f"{row['Pronoun']} {row['Present']}")
            result += " (" + ", ".join(values) + ")"
        return result

    @async_cached_property
    async def emoji(self):
        emoji = await ask(
            f"""Add single emoji for the german word '{self.word}'""",
            example="🐶",
        )

        # # deprecated
        # if (
        #     await ask(
        #         # f"""Would emoji {emoji} be suitable for the german word '{self.word}' in the dictionary? (yes/no)""",
        #         f"""Is emoji {emoji} have absolutely different meaning for the german word '{self.word}'? (yes/no)""",
        #         example="yes",
        #     )
        #     == "yes"
        # ):
        #     return "💬"
        # else:
        #     return emoji
        #
        return emoji

    @async_cached_property
    async def irregular_verb_conjugation(self):
        # - Check if the word is a verb

        is_verb = (
            await ask(
                f"""Is the german word '{self.word}' a verb? (yes/no)""",
                example="yes",
            )
            == "yes"
        )

        if not is_verb:
            return None

        # - Check if the word is an irregular verb

        is_irregular_verb = (
            await ask(f"""Is the german verb '{self.word}' an irregular verb? (yes/no)""", example="yes") == "yes"
        )

        if not is_irregular_verb:
            return None

        # - Ask for the conjugation

        irregular_present_conjugations = await ask(
            f"""Verb conjugation table for the german verb '{self.word}'""",
            example=textwrap.dedent("""
| Pronoun | Present | Irregular |
| --- | --- | --- |
| ich  | schlafe |  |
| du | schläfst | x |
| er/sie/es | schläft | x |
| wir | schlafen |  |
| ihr | schlaft |  |
| sie/Sie | schlafen |  |"""),
        )

        if " x " not in irregular_present_conjugations:
            return None

        return irregular_present_conjugations

    @async_cached_property
    async def is_irregular_verb(self):
        return await self.irregular_verb_conjugation is not None

    @async_cached_property
    async def pronunciation(self):
        result = await ask(
            f"""Add pronunciation for the german word '{self.word}'""",
            example="dɛr hʊnt",
        )

        if not isinstance(result, str):
            return ""

        return result

    @async_cached_property
    async def plural(self):
        return await ask(
            f"""Add plural for the german word '{self.word}'. If not a noun, leave empty.""",
            example="Hunde",
        )

    @async_cached_property
    async def notion_page(self):
        # - Build properties

        result = {
            "properties": {
                "word": {"title": [{"text": {"content": self.word}}]},
                "original": {"rich_text": [{"text": {"content": await self.original}}]},
                "groups": {"multi_select": [{"name": group} for group in self.groups]},
                "bundles": {"multi_select": [{"name": bundle} for bundle in self.bundles]},
                "translation": {"rich_text": [{"text": {"content": await self.translation}}]},
                "emoji": {"rich_text": [{"text": {"content": await self.emoji}}]},
                "pronunciation": {"rich_text": [{"text": {"content": await self.pronunciation}}]},
                "is_irregular_verb": {"checkbox": await self.is_irregular_verb},
            },
            "children": None,
            # if not await self.irregular_verb_conjugation
            # else [
            #     EnrichedNotionAsyncClient.parse_markdown_table(
            #         await self.irregular_verb_conjugation,
            #         annotations=lambda header, row: {"color": "red"} if row["Irregular"] == "x" else None,
            #     )
            # ],
        }

        # - Filter out None values

        return {k: v for k, v in result.items() if v is not None}


def test():
    async def main():
        Deps.load()
        word = Word(
            word="laufen",
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
