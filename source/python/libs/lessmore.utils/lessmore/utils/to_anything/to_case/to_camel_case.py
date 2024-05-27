from typing import Optional

from more_itertools import mark_ends

from lessmore.utils.to_anything.to_case.split_words import split_words


def to_camel_case(string: str, upper_case_words: Optional[list] = None) -> str:
    # - Preprocess arguments

    upper_case_words = upper_case_words or []
    upper_case_words = [word.upper() for word in upper_case_words]

    # - Split by words

    words = split_words(string, upper_case_words=upper_case_words)

    new_words = []
    for is_first, is_last, word in mark_ends(words):
        if word.upper() in upper_case_words:
            new_words.append(word.upper())
        else:
            if is_first:
                new_words.append(word.lower())
            else:
                new_words.append(word.capitalize())

    return "".join(new_words)


def test():
    assert to_camel_case("FooBar") == "fooBar"
    assert to_camel_case("fooBar") == "fooBar"
    assert to_camel_case("Foo Bar") == "fooBar"
    assert to_camel_case("foo-bar") == "fooBar"
    assert to_camel_case("FOO-BAR") == "fooBar"
    assert to_camel_case("FOO_BAR") == "fooBar"
    assert to_camel_case("fooBAR", upper_case_words=["BAR"]) == "fooBAR"


if __name__ == "__main__":
    test()
