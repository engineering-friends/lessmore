import json

from learn_language_magic.ask import ask
from lessmore.utils.lazy_dataclass import lazy_dataclass


@lazy_dataclass
class Word:
    word: str
    origin: str
    group: str
    translation_en: str = lambda self: ask(
        f"Translation of the german word '{self.word}' in English. Remove the trailing dot. Keep it as short as possible, preferably one word:"
    )
    translation_ru: str = lambda self: ask(
        f"Переведи немецкое слово '{self.word}' на русский язык. Без точки в конце. Объясни как можно кратче, предпочтительно одним словом:"
    )
    example_sentence: str = lambda self: ask(
        f"Example sentence with the german word '{self.word}'. Remove the trailing dot. Just the sentence:"
    )
    part_of_speech: str = lambda self: ask(
        f"""Part of speech of german word '{self.word}'. One of "Noun", "Verb", "Adjective", "Adverb", "Pronoun", "Preposition", "Conjunction", "Interjection" or "None".""",
        json_template='{"answer": "Noun"}',
    )
    gender: str = lambda self: ask(
        f"""Gender of the german word: '{self.word}'. One of "Masculine", "Feminine", "Neuter" or "Plural" or "None""",
        json_template='{"answer": "Masculine"}',
    )
    plural_form: str = lambda self: ask(
        f"Plural form of the german word '{self.word}'. If not applicable, answer ''",
        json_template='{"answer": "Hunde"}',
    )
    irregular_verb: bool = (
        lambda self: ask(
            f"Is '{self.word}' an irregular verb?",
            json_template='{"answer": "yes"}',
        )
        == "yes"
    )
    pronunciation: str = lambda self: ask(
        f"Pronunciation of '{self.word}'",
        json_template='{"answer": "/ˈlaʊfə/"}',
    )

    def build_notion_properties(self):
        return {
            "word": {"title": [{"text": {"content": self.word}}]},
            "origin": {"select": {"name": self.origin}},
            "group": {"select": {"name": self.group}},
            "translation_en": {"rich_text": [{"text": {"content": self.translation_en}}]},
            "translation_ru": {"rich_text": [{"text": {"content": self.translation_ru}}]},
            "example_sentence": {"rich_text": [{"text": {"content": self.example_sentence}}]},
            "part_of_speech": {"select": {"name": self.part_of_speech}},
            "gender": {"select": {"name": self.gender}},
            "plural_form": {"rich_text": [{"text": {"content": self.plural_form}}]},
            "irregular_verb": {"checkbox": self.irregular_verb},
            "pronunciation": {"rich_text": [{"text": {"content": self.pronunciation}}]},
        }


def test():
    print(
        json.dumps(
            Word(
                word="hund",
                origin="test",
                group="test",
            ).to_dict(),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    test()
