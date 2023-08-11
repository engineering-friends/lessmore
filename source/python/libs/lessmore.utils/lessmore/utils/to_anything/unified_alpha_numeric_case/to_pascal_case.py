from typing import Optional

from deeplay.utils.unified import to_camel_case
from inline_snapshot import snapshot

from lessmore.utils.run_inline_snapshot_tests.run_inline_snapshot_tests import run_inline_snapshot_tests


def to_pascal_case(string: str, upper_case_words: Optional[list] = None) -> str:
    cameled = to_camel_case(string, upper_case_words=upper_case_words)
    return cameled[0].upper() + cameled[1:]


def test():
    assert to_pascal_case("FooBar") == "FooBar"
    assert to_pascal_case("fooBar") == "FooBar"
    assert to_pascal_case("Foo Bar") == "FooBar"
    assert to_pascal_case("foo-bar") == "FooBar"
    assert to_pascal_case("FOO-BAR") == "FooBar"
    assert to_pascal_case("FOO_BAR") == "FooBar"
    assert to_pascal_case("fooBAR", upper_case_words=["BAR"]) == "FooBAR"


if __name__ == "__main__":
    run_inline_snapshot_tests(mode="failing")
