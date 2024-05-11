import json
import os
import urllib

from datetime import datetime

import cv2
import numpy as np
import PIL
import tqdm

from deeplay.utils.file_utils.read_file import read_file
from discord_to_telegram_forwarder.playground.generate_image_description import generate_image_description
from openai import OpenAI


# todo later: add a function to generate a story from a message [@marklidenberg]
# todo maybe: asdf [@marklidenberg]
# todo next: asdfasdf asdfasdf [@marklidenberg]


def generate_image(prompt: str):
    # - Create image

    return OpenAI().images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )


def test():
    # response = generate_image('''You can send prompts in OpenAI Whisper to indicate the correct spelling of certain words, and there may be a limit on the size of the dictionary, but experimentation is possible.''')
    # import webbrowser
    # webbrowser.open(response.data[0].url)

    # - Define prompt

    prompt_template = """I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS: Pixel Art, LOW DETAILS: {text}"""

    output_directory = "images/" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "/"
    os.makedirs(output_directory, exist_ok=True)

    for i, message in tqdm.tqdm(enumerate(read_file(filename="messages.json", reader=json.load)[:20])):
        # - Get story

        description = generate_image_description(message)

        # - Generate image

        response = generate_image(prompt_template.format(text=description))

        # - Lot image

        url = response.data[0].url
        with urllib.request.urlopen(url) as url_response:
            image = np.array(PIL.Image.open(url_response))

        # - Save image to file

        filename = output_directory + f"{i}_image.png"
        cv2.imwrite(filename, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # - Save metadata to yaml file

        metadata = {
            "message": message,
            "description": description,
            "revised_prompt": response.data[0].revised_prompt,
        }

        # dump yaml file

        with open(output_directory + f"{i}_metadata.txt", "w") as f:
            for key, value in metadata.items():
                f.write(f"# {key}\n\n{value}\n\n")


if __name__ == "__main__":
    test()
