import json

from learn_language_magic.ask import ask
from lessmore.utils.lazy_dataclass import lazy_dataclass


@lazy_dataclass
class Word:
    word: str
    origin: str
    origin_text: str
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
        template='"Noun"',
    )
    gender: str = lambda self: ask(
        f"""Gender of the german word: '{self.word}'. One of "Masculine", "Feminine", "Neuter" or "Plural" or "None""",
        template='"Masculine"',
    )
    plural_form: str = lambda self: ask(
        f"Plural form of the german word '{self.word}'. If not applicable, answer ''",
        template='"Hunde"',
    )
    irregular_verb: bool = (
        lambda self: ask(
            f"Is '{self.word}' an irregular verb?",
            template='"yes"',
        )
        == "yes"
    )
    pronunciation: str = lambda self: ask(
        f"Pronunciation of '{self.word}'",
        template='"/ˈlaʊfə/"',
    )

    cases: dict = (
        lambda self: ask(
            f"""Cases of the german word: '{self.word}' as a markdown table""",
            template={
                "columns": ["Case", "Irregular", "Singular", "Plural"],
                "rows": [
                    ["Nominative", "x", "der Mann", "die Männer"],
                    ["Accusative", "x", "den Mann", "die Männer"],
                    ["Dative", "x", "dem Mann", "den Männern"],
                    ["Genitive", "x", "des Mannes", "der Männer"],
                ],
            },
        )
        if self.part_of_speech == "Noun"
        else {}
    )

    conjugations: dict = (
        lambda self: ask(
            f"""Conjugations of the german word: '{self.word}' as a markdown table""",
            template="""{"columns":["Tense","Irregular Form","Pronoun","Conjugation"],"rows":{"Present (Präsens)":[["x","ich","laufe"],["x","du","läufst"],["x","er/sie/es","läuft"],["","wir","laufen"],["","ihr","lauft"],["","sie/Sie","laufen"]],"Past (Präteritum)":[["x","ich","lief"],["x","du","liefst"],["x","er/sie/es","lief"],["x","wir","liefen"],["x","ihr","lieft"],["x","sie/Sie","liefen"]],"Present Perfect (Perfekt)":[["x","ich","bin gelaufen"],["x","du","bist gelaufen"],["x","er/sie/es","ist gelaufen"],["x","wir","sind gelaufen"],["x","ihr","seid gelaufen"],["x","sie/Sie","sind gelaufen"]],"Past Perfect (Plusquamperfekt)":[["x","ich","war gelaufen"],["x","du","warst gelaufen"],["x","er/sie/es","war gelaufen"],["x","wir","waren gelaufen"],["x","ihr","wart gelaufen"],["x","sie/Sie","waren gelaufen"]],"Future I (Futur I)":[["","ich","werde laufen"],["","du","wirst laufen"],["","er/sie/es","wird laufen"],["","wir","werden laufen"],["","ihr","werdet laufen"],["","sie/Sie","werden laufen"]],"Future II (Futur II)":[["","ich","werde gelaufen sein"],["","du","wirst gelaufen sein"],["","er/sie/es","wird gelaufen sein"],["","wir","werden gelaufen sein"],["","ihr","werdet gelaufen sein"],["","sie/Sie","werden gelaufen sein"]],"Conditional II (Konjunktiv II) – Present":[["x","ich","liefe"],["x","du","liefest"],["x","er/sie/es","liefe"],["x","wir","liefen"],["x","ihr","liefet"],["x","sie/Sie","liefen"]],"Conditional II (Konjunktiv II) – Past":[["x","ich","wäre gelaufen"],["x","du","wärst gelaufen"],["x","er/sie/es","wäre gelaufen"],["x","wir","wären gelaufen"],["x","ihr","wärt gelaufen"],["x","sie/Sie","wären gelaufen"]],"Subjunctive I (Konjunktiv I) – Present":[["","ich","laufe"],["","du","laufest"],["","er/sie/es","laufe"],["","wir","laufen"],["","ihr","laufet"],["","sie/Sie","laufen"]],"Subjunctive I (Konjunktiv I) – Past":[["","ich","sei gelaufen"],["","du","seiest gelaufen"],["","er/sie/es","sei gelaufen"],["","wir","seien gelaufen"],["","ihr","seiet gelaufen"],["","sie/Sie","seien gelaufen"]],"Imperative (Befehlsform)":[["","du","lauf"],["","ihr","lauft"],["","Sie","laufen Sie"]]}}""",
        )
        if self.part_of_speech == "Verb"
        else {}
    )

    def build_notion_page_properties(self):
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

    def build_notion_page_children(self):
        result = []

        # - Build context

        if self.origin_text:
            result += [
                {
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"text": {"content": "Context"}}]},
                }
            ]

            result += [
                {
                    "type": "paragraph",
                    "paragraph": {
                        "text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": ask(
                                        f"""Extract a couple of context sentences of word "{self.word}" from this text: {self.origin_text}""",
                                        template='"Mr Dursley was the director of a firm called Grunnings, which made drills"',
                                    ),
                                },
                            }
                        ]
                    },
                }
            ]

        # - Build cases

        if self.cases:
            # - Add heading "Cases"

            result += [
                {
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"text": {"content": "Cases"}}]},
                }
            ]

            # - Add simple table

            """
            | Case | Irregular | Singular | Plural |
            | --- | --- | --- | --- |
            | Nominative | x | der Mann | die Männer |
            | Accusative | x | den Mann | die Männer |
            | Dative | x | dem Mann | den Männern |
            | Genitive | x | des Mannes | der Männer |
                """

            # - Add table

            result += [
                {
                    "type": "table",
                    "table": {
                        "table_width": 4,
                        "has_column_header": True,
                        "has_row_header": False,
                        "children": [
                            {
                                "type": "table_row",
                                "table_row": {
                                    "cells": [
                                        [
                                            {
                                                "type": "text",
                                                "text": {"content": cell},
                                            }
                                        ]
                                        for cell in row
                                    ]
                                },
                            }
                            for row in [self.cases["columns"]] + self.cases["rows"]
                        ],
                    },
                }
            ]

        # - Build conjugations

        if self.conjugations:
            # - Add heading "Conjugations"

            result += [
                {
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"text": {"content": "Conjugations"}}]},
                }
            ]

            # - Add simple table

            """
            | Tense | Irregular Form | Pronoun | Conjugation |
            | --- | --- | --- | --- |
            | Present (Präsens) | x | ich | laufe |
            | Present (Präsens) | x | du | läufst |
            ...
            """
            result += [
                {
                    "type": "table",
                    "table": {
                        "table_width": 4,
                        "has_column_header": True,
                        "has_row_header": False,
                        "children": [
                            {
                                "type": "table_row",
                                "table_row": {
                                    "cells": [
                                        [
                                            {
                                                "type": "text",
                                                "text": {"content": cell},
                                            }
                                        ]
                                        for cell in row
                                    ]
                                },
                            }
                            for row in [self.conjugations["columns"]]
                            + [[key] + row for key, rows in self.conjugations["rows"].items() for row in rows]
                        ],
                    },
                }
            ]

        return result


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
