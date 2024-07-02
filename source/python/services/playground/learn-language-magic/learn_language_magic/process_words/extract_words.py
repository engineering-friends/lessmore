import json

from learn_language_magic.process_words.ask import ask
from openai.types.chat.completion_create_params import ResponseFormat


def extract_words(text: str):
    PROMPT = """
    [Instructions]
    - I want you to extract all words or idiomatic expressions from this text in a normalized form
    - Return format: json list
    - Keep original language 

    [Example] 
    Input: `Jobs are just a piece of cake`
    Output: {{"words": ["job", "be", "just", "a", "piece of cake"]}}
    
    [Text]
    {text}"""

    return ask(
        prompt=PROMPT.format(text=text),
        dedent=True,
        open_ai_kwargs={
            "response_format": ResponseFormat(type="json_object"),
            "model": "gpt-4o",
        },
    )


def test():
    text = "Hello, world!"
    assert json.loads(extract_words(text)) == {"words": ["hello", "world"]}
    print("All tests passed.")


if __name__ == "__main__":
    test()
