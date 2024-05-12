import json
import os
import urllib

from datetime import datetime

import cv2
import numpy as np
import pandas as pd
import PIL
import tqdm

from deeplay.utils.file_utils.read_file import read_file
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.cache_on_disk import (
    cache_on_disk,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.generate_image import (
    generate_image,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.plot_dataframe_of_images import (
    plot_dataframe_of_images,
)
from utils_ak.os import open_file_in_os


def generate_images(
    texts: list[str],
    text_prompts_by_label: dict,
    image_prompts_by_label: dict,
) -> pd.DataFrame:  # label, text, filename
    # - Run image generation

    print("Generating images")
    for text_prompt_label, text_prompt in tqdm.tqdm(list(text_prompts_by_label.items())):
        print("text_prompt_label:", text_prompt_label)
        for image_prompt_label, image_prompt in image_prompts_by_label.items():
            print("image_prompt_label:", image_prompt_label)
            for i, text in enumerate(tqdm.tqdm(texts)):
                # - Define output directory and filename

                output_directory = f"generated_images/{text_prompt_label}--{image_prompt_label}"
                os.makedirs(output_directory, exist_ok=True)
                filename = f"{output_directory}/{i}.png"

                # - Skip if file exists

                if os.path.exists(filename):
                    continue

                # - Generate image

                image_contents, revised_prompt = cache_on_disk()(generate_image)(
                    text=text,
                    image_prompt=image_prompt,
                    image_description_prompt=text_prompt,
                    keep_original_prompt=True,
                )

                # - Save image to file

                image = np.array(PIL.Image.open(image_contents))

                cv2.imwrite(filename, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

                # - Save metadata to yaml file

                metadata = {
                    "text": text,
                    "revised_prompt": revised_prompt,
                }

                # dump yaml file

                with open(f"{output_directory}/{i}_metadata.txt", "w") as f:
                    for key, value in metadata.items():
                        f.write(f"# {key}\n\n{value}\n\n")

    # - Collect results and plot grid

    print("Collecting results and plotting grid")
    values = []
    for text_prompt_label, text_prompt in text_prompts_by_label.items():
        for image_prompt_label, image_prompt in image_prompts_by_label.items():
            for i, text in enumerate(texts):
                output_directory = f"generated_images/{text_prompt_label}--{image_prompt_label}"
                filename = f"{output_directory}/{i}.png"
                values.append([f"{text_prompt_label}_{image_prompt_label}", filename, text])
    df = pd.DataFrame(values, columns=["label", "filename", "text"])

    # make label as index, text as columns
    df = df.pivot(index="label", columns="text", values="filename")

    return df


def test():
    df = generate_images(
        texts=read_file(filename="data/messages.json", reader=json.load)[:10],
        # texts=[
        #     """Escape the Draft: One Man's Elaborate Quest to Deregister from Military Service and Navigate the Maze of Bureaucracy"""
        # ],
        text_prompts_by_label={
            # "basic": "Describe in one small sentence, no more than 10 words: ",
            # "key_detail": "Extract key detail from the text in one sentence, no more than 10 words: ",
            # "essence": "In one sentence, describe the essence of the text: ",
            # "movie_shot": "Suppose that this text is a shot in a movie. Describe the shot in one sentence: ",  # too many text
            # "movie_title": "If this text was a movie, what would be the title of the movie?: ",  # great!
            # "no_text_prompt": ""
            "title_10plus_words1": """If this text was a movie, what would be the title in 10+ words of the movie?
                Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)  
                Just the title:"""
        },
        image_prompts_by_label={
            "pixel_art_low_details": "Pixel Art, LOW DETAILS:",
            # "no_text_test1": "Pixel Art, pictogram",
            # "no_text_test3": "Pixel Art, abstract",
            # "no_text_test4": "Pixel Art, solid",
            "no_text_test2": "Pixel Art, vector",
            "no_text_test5": "Pixel Art, minimal",
            "no_text_test6": "Pixel Art, NO TEXT",
            "no_text_test6_2": "Pixel Art, ZERO TEXT",
            "no_text_test7": "Pixel Art, in a world where people are blind",
            # "no_text_test8": "Pixel Art, a poster for blind people",
            # "no_text_test9": "Pixel Art, a poster for people with dyslexia",
        },
    )
    grid_filename = f"grids/{datetime.now()}.png"
    os.makedirs("grids", exist_ok=True)
    plot_dataframe_of_images(df=df, output_filename=grid_filename)
    open_file_in_os(grid_filename)


if __name__ == "__main__":
    test()
