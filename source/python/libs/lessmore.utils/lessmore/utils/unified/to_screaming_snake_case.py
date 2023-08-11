def to_screaming_snake_case(string: str, upper_case_words: Optional[list] = None) -> str:
    return to_snake_case(string, upper_case_words=upper_case_words).upper()
