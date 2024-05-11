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
    print(generate_image_description("""New tools in Deeplay available"""))

    # - Check with all messages

    for message in read_file(filename="data/messages.json", reader=json.load)[:10]:
        if not message:
            continue
        print(message)
        print("-" * 20)
        print(generate_image_description(message))
        print("=" * 20)


if __name__ == "__main__":
    test()
