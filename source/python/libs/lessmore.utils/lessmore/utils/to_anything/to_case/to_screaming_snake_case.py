from typing import Optional

from deeplay.utils.unified import to_snake_case


def to_screaming_snake_case(string: str, upper_case_words: Optional[list] = None) -> str:
    return to_snake_case(string, upper_case_words=upper_case_words).upper()


def test():
    assert to_screaming_snake_case("FooBar") == "FOO_BAR"
    assert to_screaming_snake_case("fooBar") == "FOO_BAR"
    assert to_screaming_snake_case("Foo Bar") == "FOO_BAR"
    assert to_screaming_snake_case("foo-bar") == "FOO_BAR"
    assert to_screaming_snake_case("FOO-BAR") == "FOO_BAR"
    assert to_screaming_snake_case("FOO_BAR") == "FOO_BAR"
    assert to_screaming_snake_case("fooBAR", upper_case_words=["BAR"]) == "FOO_BAR"


if __name__ == "__main__":
    test()
