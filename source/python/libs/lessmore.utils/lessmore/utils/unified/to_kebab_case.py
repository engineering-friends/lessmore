from typing import Optional

from lessmore.utils.unified.to_snake_case import to_snake_case


def to_kebab_case(string: str, upper_case_words: Optional[list] = None) -> str:
    return to_snake_case(string, upper_case_words=upper_case_words).replace("_", "-")


import pytest

from inline_snapshot import snapshot


def test_something():
    assert 1548 * 18489 == snapshot()


if __name__ == "__main__":
    pytest.main([__file__], ["--update-snapshots=new"])
