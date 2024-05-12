import json

from deeplay.utils.file_utils.read_file import read_file
from openai import OpenAI


def generate_image_description2(text: str) -> str:
    # - Extract 3-5 tags from the text

    tags = (
        OpenAI()
        .chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": """Extract 3-5 tags from the text, return them separated by commas, translated to English
                    
                    Example: Russia, military, documents, escape
                    
                    Text:
                    """
                    + text,
                },
            ],
        )
        .choices[0]
        .message.content
    )

    print("tags:", tags)

    # - Generate the description

    story = (
        OpenAI()
        .chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": """Make up a simple story in English in 2-3 sentences that should match those tags. : 
                    """
                    + tags,
                },
            ],
        )
        .choices[0]
        .message.content
    )
    print("story:", story)

    # - Get description

    description = (
        OpenAI()
        .chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": """Make a book illustration for one episode of this story, 15 words max. NO SCREENS OR COMPUTERS ON ILLUSTRATION. A story:
                    """
                    + story,
                },
            ],
        )
        .choices[0]
        .message.content
    )

    return description


def test():
    # - Single run

    # print(
    #     generate_image_description(
    #         text="""Escape the Draft. A man documents his meticulous journey to deregister from military service, detailing the bureaucratic hurdles and the strategic gathering of documents required to achieve his goal.""",
    #         prompt="A movie title in 10+ words",
    #     )
    # )

    # - Check with all messages

    for message in read_file(filename="data/messages.json", reader=json.load)[:10]:
        if not message:
            continue
        print("-" * 20)
        print(
            generate_image_description2(
                message,
            )
        )


if __name__ == "__main__":
    test()
