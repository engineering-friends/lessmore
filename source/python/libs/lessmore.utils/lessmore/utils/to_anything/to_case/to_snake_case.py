from typing import Optional

from lessmore.utils.to_anything.to_case.split_words import split_words


def to_snake_case(string: str, upper_case_words: Optional[list] = None) -> str:
    words = split_words(string, upper_case_words=upper_case_words)
    words = [word.lower() for word in words]
    return "_".join(words)


def test():
    assert to_snake_case("FooBar") == "foo_bar"
    assert to_snake_case("fooBar") == "foo_bar"
    assert to_snake_case("Foo Bar") == "foo_bar"
    assert to_snake_case("foo-bar") == "foo_bar"
    assert to_snake_case("FOO-BAR") == "foo_bar"
    assert to_snake_case("FOO_BAR") == "foo_bar"
    assert to_snake_case("fooBAR", upper_case_words=["BAR"]) == "foo_bar"


if __name__ == "__main__":
    test()
