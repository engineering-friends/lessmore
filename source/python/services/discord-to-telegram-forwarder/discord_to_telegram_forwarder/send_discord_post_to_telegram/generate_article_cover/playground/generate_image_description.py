import json

from deeplay.utils.file_utils.read_file import read_file
from openai import OpenAI


def generate_image_description(
    text: str,
    prompt: str = "Describe in one small sentence, no more than 10 words: ",
) -> str:
    return (
        OpenAI()
        .chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "\n".join([prompt + text]).strip(),
                },
            ],
        )
        .choices[0]
        .message.content
    )


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

        # print(message)
        print("-" * 20)
        print(
            generate_image_description(
                message,
                # prompt="""If this text was a movie, what would be the title and one-sentence description of the movie?
                # Skip any names, use abstract forms (e.g. Petr Lavrov -> a man)
                # Just the title:""",
                prompt="""If this text was a movie, what would be the title in 10+ words of the movie?
                Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)  
                Just the title:""",
            )
        )
        print("=" * 20)


if __name__ == "__main__":
    test()
