import asyncio
import json
import re
import textwrap

from dataclasses import dataclass

from benedict import benedict
from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from learn_language_magic.draw_card_image.draw_card_image import draw_card_image
from lessmore.utils.asynchronous.async_cached_property import async_cached_property, prefetch_all_cached_properties
from lessmore.utils.asynchronous.gather_nested import gather_nested
from lessmore.utils.read_config.merge_dicts import merge_dicts
from more_itertools import mark_ends


@dataclass
class Word:
    word: str
    origin: str
    origin_text: str
    groups: list[str]

    @async_cached_property
    async def inline_translation_with_colored_genders(self):
        # - Extract distinct words

        words = await ask(
            f"Extract distinct words from the german phrase `{self.word}`, skip und and articles",
            example=["Apfel", "Orange", "trinken"],
        )
        words = [f"- {word}" for word in words]

        async def _process_word(word):
            word = await ask(
                f"""Add english translation and pronunciation for '{word}'. Remove the trailing dot. Keep it as short as possible. Skip `und`, add articles if needed""",
                example="- der Hund (dog, /dɛr hʊnt/)",
            )

            if all(pronoun not in word for pronoun in ["der", "die", "das"]):
                return [{"text": {"content": word + "\n"}}]

            # - Get nouns

            translation = await ask(f"Translation of the german '{word}' in Russian", example="Машина")
            russian_pronoun = await ask(
                f"`{translation} - это он, она или оно?",
                example="он",
            )
            russian_pronoun = russian_pronoun.lower()

            if russian_pronoun not in ["он", "она", "оно"]:
                return [{"text": {"content": word + "\n"}}]

            german_pronoun = re.search(r"\bder\b|\bdie\b|\bdas\b", word.lower())

            if not german_pronoun:
                return [{"text": {"content": word + "\n"}}]

            german_pronoun = german_pronoun.group()

            is_gender_same = (
                (russian_pronoun == "он" and german_pronoun == "der")
                or (russian_pronoun == "она" and german_pronoun == "die")
                or (russian_pronoun == "оно" and german_pronoun == "das")
            )

            # - Split text by nouns and non-nouns  ("der Apfel (apple) und die Orange (orange)" -> ["der", " Apfel (apple) und ", "die", " Orange (orange)"])

            def split_preserve_separator(text, separator):
                escaped_separator = re.escape(separator)
                return re.split(f"(?<={escaped_separator})|(?={escaped_separator})", text)

            parts = split_preserve_separator(word, german_pronoun)
            parts = sum([split_preserve_separator(part, german_pronoun.title()) for part in parts], [])

            # - Build result

            result = []

            for is_first, is_last, part in mark_ends(parts):
                text = part if not is_last else part + "\n"

                if part.lower() == german_pronoun:
                    if not is_gender_same:
                        result.append(
                            {
                                "annotations": {"color": "red"},
                                "plain_text": text,
                                "text": {"content": text},
                            }
                        )
                    else:
                        result.append(
                            {
                                "annotations": {"color": "green"},
                                "plain_text": text,
                                "text": {"content": text},
                            }
                        )
                else:
                    result.append({"text": {"content": text}})
            return result

        # - Process words

        return sum(await asyncio.gather(*[_process_word(word) for word in words]), [])

    @async_cached_property
    async def translation_en(self):
        return await ask(
            f"Translation of the german '{self.word}' in English. Remove the trailing dot. Keep it as short as possible, preferably one-to-one:"
        )

    @async_cached_property
    async def part_of_speech(self):
        return await ask(
            f"""Parts of speech of german '{self.word}'. Each word is one of "Noun", "Verb", "Adjective", "Adverb". Skip articles, prepositions, etc.""",
            example="""der Hund (Noun) und die Katze (Noun)""",
        )

    @async_cached_property
    async def plural_form(self):
        return await ask(
            f"For all nouns from '{self.word}' provide their plural forms. Skip non-noun words. Use comma as a separator.",
            example="Hunde, Katzen, Autos",
        )

    @async_cached_property
    async def irregular_verb(self):
        return await ask(
            f"Which words from `{self.word}` are irregular? Skip non-verb words`",
            example="sein, haben, laufen",
        )

    @async_cached_property
    async def pronunciation(self):
        return await ask(
            f"Pronunciation of german phrase '{self.word}'",
            example="/ˈlaʊfə ˈhaːbn/",
        )

    @async_cached_property
    async def image_url(self):
        return await draw_card_image(word=self.word)

    @async_cached_property
    async def notion_page(self):
        # - Build properties

        result = {
            "properties": {
                "word": {"title": [{"text": {"content": self.word}}]},
                "origin": {"select": {"name": self.origin}},
                "groups": {"multi_select": [{"name": group} for group in self.groups]},
                "translation_en": {"rich_text": [{"text": {"content": await self.translation_en}}]},
                "part_of_speech": {"rich_text": [{"text": {"content": await self.part_of_speech}}]},
                "plural_form": {"rich_text": [{"text": {"content": await self.plural_form}}]},
                "irregular_verb": {"rich_text": [{"text": {"content": await self.irregular_verb}}]},
                "pronunciation": {"rich_text": [{"text": {"content": await self.pronunciation}}]},
                "refresh_image": {"checkbox": False},  # reset
                "inline_translation": {"rich_text": await self.inline_translation_with_colored_genders},
                "cover": {
                    "files": [
                        {
                            "name": f"{self.word}.png",
                            "type": "external",
                            "external": {"url": await self.image_url},
                        }
                    ],
                },
            },
            "children": [],  # will be filled later
        }

        if not self.groups:
            result["properties"].pop("groups")

        # - Add children

        children = []

        # -- Add image

        children += [
            {
                "type": "image",
                "image": {
                    "type": "external",
                    "external": {"url": await self.image_url},
                },
            }
        ]

        # -- Build context

        if self.origin_text:
            children += [
                {
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"text": {"content": "Context"}}]},
                }
            ]

            children += [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": await ask(
                                        f"""Extract a couple of context sentences of word "{self.word}" from this text: {self.origin_text}""",
                                        example="Mr Dursley was the director of a firm called Grunnings, which made drills",
                                    ),
                                },
                            }
                        ]
                    },
                }
            ]

        result["children"] = children

        # - Filter out None values

        return {k: v for k, v in result.items() if v is not None}


def test():
    async def main():
        Deps.load()
        word = Word(
            word="hunds",
            origin="test",
            origin_text="",
            groups=["test"],
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
