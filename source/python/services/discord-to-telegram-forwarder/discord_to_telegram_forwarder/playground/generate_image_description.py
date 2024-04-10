from deeplay.utils.file_utils.read_file import read_file
from openai import OpenAI


def generate_image_description(text: str) -> str:
    return (
        OpenAI()
        .chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": """
: Read this article and write one small sentence, no more than 10 words, that characterizes this article. Article: {text}""".format(
                        text=text
                    ).strip(),
                },
            ],
        )
        .choices[0]
        .message.content
    )


def test():
    print(generate_image_description("""New tools in Deeplay availble"""))

    # - Check with all messages

    for message in read_file(path="messages.json", reader=json.load):
        if not message:
            continue
        print(message)
        print("-" * 20)
        print(generate_a_story(message))
        print("=" * 20)


if __name__ == "__main__":
    test()
