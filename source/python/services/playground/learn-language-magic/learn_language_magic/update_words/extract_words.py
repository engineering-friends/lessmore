from learn_language_magic.ask import ask


def extract_words(text: str):
    PROMPT = """
    [Instructions]
    - I want you to extract all words or idiomatic expressions from this text in a normalized form
    - Keep original language 

    [Example] 
    Input: `Jobs are just a piece of cake`
    Output: {{"words": ["job", "be", "just", "a", "piece of cake"]}}
    
    [Text]
    {text}"""

    return ask(prompt=PROMPT.format(text=text), template={"words": ["job", "be", "just", "a", "piece of cake"]})


def test():
    text = "Hello, world!"
    assert extract_words(text) == {"words": ["hello", "world"]}
    print("All tests passed.")


if __name__ == "__main__":
    test()
