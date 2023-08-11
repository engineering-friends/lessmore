def to_pascal_case(string: str, upper_case_words: Optional[list] = None) -> str:
    cameled = to_camel_case(string, upper_case_words=upper_case_words)
    return cameled[0].upper() + cameled[1:]
