import asyncio

from learn_language_magic.ask import ask


async def extract_words(text: str):
    PROMPT = """
    [Instructions]
    - I want you to extract all words or idiomatic expressions from this text in a normalized form
    - Keep original language 

    [Example] 
    Input: `Jobs are just a piece of cake`
    Output: {{"words": ["job", "be", "just", "a", "piece of cake"]}}
    
    [Text]
    {text}"""

    return await ask(prompt=PROMPT.format(text=text), template=["job", "be", "just", "a", "piece of cake"])


def test():
    async def main():
        # german
        text = "Hallo Welt"
        assert await extract_words(text) == {"words": ["hallo", "welt"]}
        print("All tests passed.")

    asyncio.run(main())


if __name__ == "__main__":
    test()
