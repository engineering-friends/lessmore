import asyncio
import json

from dataclasses import dataclass

from benedict import benedict
from learn_language_magic.ask import ask
from learn_language_magic.deps import Deps
from learn_language_magic.draw_card_image.draw_card_image import draw_card_image
from lessmore.utils.asynchronous.async_cached_property import async_cached_property, prefetch_all_cached_properties
from lessmore.utils.asynchronous.gather_nested import gather_nested
from lessmore.utils.read_config.merge_dicts import merge_dicts


@dataclass
class Word:
    word: str
    origin: str
    origin_text: str
    groups: list[str]

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
    async def different_genders(self):
        # - Get nouns

        nouns = await ask(f"Extract nouns from german `{self.word}`", example=["der Hund", "die Katze"])

        russian_translations = await asyncio.gather(
            *[ask(f"Translation of the german '{noun}' in Russian", example="Машина") for noun in nouns]
        )

        russian_pronouns = await asyncio.gather(
            *[ask(f"`{translation} это он, она или оно?`", example="он") for translation in russian_translations]
        )

        # - Build result

        values = []

        for i in range(len(nouns)):
            if "die" in nouns[i] and russian_pronouns[i] != "она":
                values.append(f"{nouns[i]} ({russian_translations[i]} {russian_pronouns[i]})")
            elif "der" in nouns[i] and russian_pronouns[i] != "он":
                values.append(f"{nouns[i]} ({russian_translations[i]} {russian_pronouns[i]})")
            elif "das" in nouns[i] and russian_pronouns[i] != "оно":
                values.append(f"{nouns[i]} ({russian_translations[i]} {russian_pronouns[i]})")
        return ", ".join(values)

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
                "different_genders": {"rich_text": [{"text": {"content": await self.different_genders}}]},
                "refresh_image": {"checkbox": False},  # reset
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
