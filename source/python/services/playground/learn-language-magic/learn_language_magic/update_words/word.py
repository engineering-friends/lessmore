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
    async def translation_ru(self):
        return await ask(
            f"Переведи немецкое '{self.word}' на русский язык. Без точки в конце. Объясни как можно кратче, предпочтительно один-к-одному:"
        )

    @async_cached_property
    async def example_sentence(self):
        return await ask(f"Example sentence with the german '{self.word}'. Remove the trailing dot. Just the sentence:")

    @async_cached_property
    async def part_of_speech(self):
        return await ask(
            f"""Parts of speech of german '{self.word}'. Each word is one of "Noun", "Verb", "Adjective", "Adverb", "Pronoun", "Preposition", "Conjunction", "Interjection" or "None".""",
            template="Noun",
        )

    @async_cached_property
    async def gender(self):
        result = await ask(
            f"""Gender of the german '{self.word}'. Each word is one of "Masculine", "Feminine", "Neuter" or "Plural" or "None""",
            template="Masculine",
        )

        return result

    @async_cached_property
    async def plural_form(self):
        return await ask(
            f"Plural form of the german '{self.word}'. If not applicable, answer ''",
            template="Hunde",
        )

    @async_cached_property
    async def irregular_verb(self):
        return (
            await ask(
                f"Is german '{self.word}' have irregular verbs? Which? Just words",
                template="yes",
            )
            == "yes"
        )

    @async_cached_property
    async def pronunciation(self):
        return await ask(
            f"Pronunciation of german '{self.word}'",
            template="/ˈlaʊfə/",
        )

    @async_cached_property
    async def different_gender(self):
        return await ask(
            f"Is german '{self.word}' have different genders from Russian? Which? For each different gender write `die Sonne / солнце (оно)`",
            template="die Sonne / солнце (оно), der Mond / луна (она)",
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
                "translation_ru": {"rich_text": [{"text": {"content": await self.translation_ru}}]},
                "example_sentence": {"rich_text": [{"text": {"content": await self.example_sentence}}]},
                "part_of_speech": {"rich_text": [{"text": {"content": await self.part_of_speech}}]},
                "gender": {"rich_text": [{"text": {"content": await self.gender}}]},
                "plural_form": {"rich_text": [{"text": {"content": await self.plural_form}}]},
                "irregular_verb": {"rich_text": [{"text": {"content": await self.irregular_verb}}]},
                "pronunciation": {"rich_text": [{"text": {"content": await self.pronunciation}}]},
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

        if not await self.gender:
            result["properties"].pop("gender")

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
                                        template="Mr Dursley was the director of a firm called Grunnings, which made drills",
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
