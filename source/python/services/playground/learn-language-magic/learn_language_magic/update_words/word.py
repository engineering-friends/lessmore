from lessmore.utils.lazy_dataclass import lazy_dataclass


@lazy_dataclass
class Word:
    word: str
    origin: str
    group: str
    translation_en: str
    translation_ru: str
    example_sentence: str
    part_of_speech: str
    gender: str
    plural_form: str
    irregular_verb: bool
    pronunciation: str
    notes: str
