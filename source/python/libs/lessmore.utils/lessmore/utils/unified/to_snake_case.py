from typing import Optional


def to_snake_case(string: str, upper_case_words: Optional[list] = None) -> str:
    words = _split_words(string, upper_case_words=upper_case_words)
    words = [word.lower() for word in words]
    return "_".join(words)
