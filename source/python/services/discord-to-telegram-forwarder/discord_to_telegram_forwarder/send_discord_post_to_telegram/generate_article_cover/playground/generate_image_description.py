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
                prompt="""
                
                - There is an animated movie with a scene, that is described below. Describe the first shot of the scene. 
                - DO NOT INCLUDE any electronic devices with screens (e.g. phones, laptops, etc.)
                - It should be ONE shot, describing ONE scene. Choose any scene from the text.
                - It MUST have describe the text briefly, including it's core idea
                - Make it 15 words max
                
                Examples of other scenes: 
                - A man is standing in the middle of the desert, looking at the sky, happy
                - The night sky full of fireworks
                - Winter landscape with houses, trees and snow covered mountain background, a sky filled with snowflakes
                - A man finishing a grueling marathon race, crowd cheering, with a mountainous backdrop.
                - Man submits documents to military office to deregister, a military officer standing right in front of him, looking ominous.
                - iPhone with Kremlin on the background 
                
                The text: 
                """,
            )
        )
        print("=" * 20)


if __name__ == "__main__":
    test()
