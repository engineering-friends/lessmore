import re

from typing import Optional

from more_itertools import split_before


def split_words(string: str, upper_case_words: Optional[list] = None) -> list[str]:
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


def test():
    assert split_words("FooBar") == ["Foo", "Bar"]
    assert split_words("fooBar") == ["foo", "Bar"]
    assert split_words("Foo Bar") == ["Foo", "Bar"]
    assert split_words("foo-bar") == ["foo", "bar"]
    assert split_words("FOO-BAR") == ["FOO", "BAR"]
    assert split_words("FOO_BAR") == ["FOO", "BAR"]
    assert split_words("fooBAR", upper_case_words=["BAR"]) == ["foo", "Bar"]


if __name__ == "__main__":
    test()
