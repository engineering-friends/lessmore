import json
import os
import urllib

from datetime import datetime

import cv2
import numpy as np
import PIL
import tqdm

from deeplay.utils.file_utils.read_file import read_file
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.generate_image_description import (
    generate_image_description,
)
from openai import OpenAI


def generate_image(text: str, image_prompt: str, image_description_prompt: str = "", keep_original_prompt: bool = True):
    # - Preprocess text if needed

    if image_description_prompt:
        text = generate_image_description(text=text, prompt=image_description_prompt)

    # - Set prompt prefix

    keep_prompt_prefix = (
        """I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"""
        if keep_original_prompt
        else ""
    )

    # - Create image

    return OpenAI().images.generate(
        model="dall-e-3",
        prompt="\n".join([keep_prompt_prefix, image_prompt, text]),
        size="1024x1024",
        quality="standard",
        n=1,
    )


def test():
    # - Get message (texts)

    texts = read_file(filename="data/messages.json", reader=json.load)[:2]

    # - Define prompts

    text_prompts_by_label = {
        "basic": "Describe in one small sentence, no more than 10 words: ",
        # "key_detail": "Extract key detail from the text in one sentence, no more than 10 words: ",
        # "essence": "In one sentence, describe the essence of the text: ",
        # "movie_shot": "Suppose that this text is a shot in a movie. Describe the shot in one sentence: ",
        # "movie_title": "If this text was a movie, what would be the title of the movie?: ",
    }

    image_prompts_by_label = {"pixel_art, low_details": "Pixel Art, LOW DETAILS:"}

    # - Run image generation

    for text_prompt_label, text_prompt in text_prompts_by_label.items():
        for image_prompt_label, image_prompt in image_prompts_by_label.items():
            for i, text in enumerate(texts):
                response = generate_image(
                    text=text,
                    image_prompt=image_prompt,
                    image_description_prompt=text_prompt,
                    keep_original_prompt=True,
                )

                # - Get output directory

                output_directory = f"output/{text_prompt_label}_{image_prompt_label}"
                os.makedirs(output_directory, exist_ok=True)

                # - Save image to file

                url = response.data[0].url
                with urllib.request.urlopen(url) as url_response:
                    image = np.array(PIL.Image.open(url_response))

                filename = f"{output_directory}/{i}.png"
                cv2.imwrite(filename, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

                # - Save metadata to yaml file

                metadata = {
                    "text": text,
                    "revised_prompt": response.data[0].revised_prompt,
                }

                # dump yaml file

                with open(f"{output_directory}/{i}_metadata.txt", "w") as f:
                    for key, value in metadata.items():
                        f.write(f"# {key}\n\n{value}\n\n")


if __name__ == "__main__":
    test()
