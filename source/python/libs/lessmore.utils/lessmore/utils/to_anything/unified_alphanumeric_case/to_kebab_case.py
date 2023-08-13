from typing import Optional

from lessmore.utils.to_anything.unified_alphanumeric_case.to_snake_case import to_snake_case


def to_kebab_case(string: str, upper_case_words: Optional[list] = None) -> str:
    return to_snake_case(string, upper_case_words=upper_case_words).replace("_", "-")


def test():
    assert to_kebab_case("FooBar") == "foo-bar"
    assert to_kebab_case("fooBar") == "foo-bar"
    assert to_kebab_case("Foo Bar") == "foo-bar"
    assert to_kebab_case("foo-bar") == "foo-bar"
    assert to_kebab_case("FOO-BAR") == "foo-bar"
    assert to_kebab_case("FOO_BAR") == "foo-bar"
    assert to_kebab_case("fooBAR", upper_case_words=["BAR"]) == "foo-bar"


if __name__ == "__main__":
    test()
