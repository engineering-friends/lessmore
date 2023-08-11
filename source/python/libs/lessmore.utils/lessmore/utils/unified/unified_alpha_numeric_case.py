import re

from typing import Optional, Sequence

from lessmore.utils.fp import mark_ends, split_before


# todo later: add support for sections: foo.barBaz -> foo.bar_baz [@marklidenberg]


def _split_words(string: str, upper_case_words: Optional[list] = None):
    # - Preprocess arguments

    upper_case_words = upper_case_words or []
    upper_case_words = [word.upper() for word in upper_case_words]

    # - Try to split by separator

    for key in ["_", "-", " "]:
        if key in string:
            words = string.split(key)
            words = [word for word in words if word]
            return words

    # - "FOO" -> ["FOO"]

    if string == string.upper():
        return [string]

    # - Split by capital letters

    # replace full upper case words with lower case
    for word in upper_case_words:
        string = re.sub(rf"([^A-Z]*){word.upper()}([^A-Z]*)", f"\g<1>{word.capitalize()}\g<2>", string)

    return ["".join(letters) for letters in split_before(string, pred=lambda s: s.isupper())]


def test_split_words():
    assert _split_words("FooBar") == ["Foo", "Bar"]
    assert _split_words("fooBar") == ["foo", "Bar"]
    assert _split_words("Foo Bar") == ["Foo", "Bar"]
    assert _split_words("foo-bar") == ["foo", "bar"]
    assert _split_words("FOO-BAR") == ["FOO", "BAR"]
    assert _split_words("FOO_BAR") == ["FOO", "BAR"]
    assert _split_words("fooBAR", upper_case_words=["BAR"]) == ["foo", "Bar"]


def to_pascal_case(string: str, upper_case_words: Optional[list] = None) -> str:
    cameled = to_camel_case(string, upper_case_words=upper_case_words)
    return cameled[0].upper() + cameled[1:]


def to_snake_case(string: str, upper_case_words: Optional[list] = None) -> str:
    words = _split_words(string, upper_case_words=upper_case_words)
    words = [word.lower() for word in words]
    return "_".join(words)


def to_kebab_case(string: str, upper_case_words: Optional[list] = None) -> str:
    return to_snake_case(string, upper_case_words=upper_case_words).replace("_", "-")


def to_screaming_snake_case(string: str, upper_case_words: Optional[list] = None) -> str:
    return to_snake_case(string, upper_case_words=upper_case_words).upper()


if __name__ == "__main__":
    test_split_words()
    test()
