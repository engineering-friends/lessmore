import json
import os
import urllib

from datetime import datetime

import cv2
import numpy as np
import pandas as pd
import PIL
import tqdm

from discord_to_telegram_forwarder.send_discord_post_to_telegram.ai.ask import ask
from discord_to_telegram_forwarder.send_discord_post_to_telegram.ai.generate_image import generate_image
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.plot_dataframe_of_images import (
    plot_dataframe_of_images,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.utils.cache_on_disk import cache_on_disk
from retry import retry

from deeplay.utils.file_utils.read_file import read_file


def _label(text: str, n_words: int = 1):
    return cache_on_disk()(ask)(prompt=f'Give a description for the template, lower case, {n_words} words: "{text}"')


def generate_covers_bulk(
    prompts: list[str],
    pre_prompts: [],
    styles: [],
) -> pd.DataFrame:  # label, text, filename
    values = []

    for prompt in tqdm.tqdm(prompts):
        for pre_prompt in pre_prompts:
            for style in styles:
                image_contents = cache_on_disk()(retry(tries=10, delay=1)(generate_image))(
                    prompt=prompt,
                    pre_prompt=pre_prompt,
                    style=style,
                )
                values.append(
                    {
                        "image": PIL.Image.open(PIL.Image.io.BytesIO(image_contents)),
                        "prompt": _label(prompt, n_words=5),
                        "index": f"{_label(pre_prompt)}--{_label(style)}",
                    }
                )
    df = pd.DataFrame(values)
    df = df[["prompt", "index", "image"]]
    df = df.pivot(index="index", columns="prompt", values="image")
    return df


def test():
    df = generate_covers_bulk(
        prompts=read_file(filename="data/messages.json", reader=json.load)[:20],
        pre_prompts=[
            # "",
            # "Describe in one small sentence, no more than 10 words: {prompt}",
            # "Extract key detail from the text in one sentence, no more than 10 words: {prompt}",
            # "If this text was a movie, what would be the title of the movie?: {prompt}",
            # "If this text was a movie, what would be the title in 10+ words of the movie?\n Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)\n Just the title: {prompt}",
            """
                    - There is an animated movie with a scene, that is described below. Describe the first shot of the scene
                    - EXCLUDE all electronic devices with screens (e.g. phones, laptops, etc.)
                    - It should be ONE shot, describing ONE scene. Choose any scene from the text
                    - It MUST have describe the text briefly, including it's core idea
                    - Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)
                    - Make it 15 words max

                    Examples of other scenes:
                    - A man is standing in the middle of the desert, looking at the sky, happy
                    - The night sky full of fireworks
                    - Winter landscape with houses, trees and snow covered mountain background, a sky filled with snowflakes
                    - A man finishing a grueling marathon race, crowd cheering, with a mountainous backdrop
                    - Man hands over documents at military registration desk, civilian officer reviews them, austere office setting
                    - Father and son discussing universities at home, papers with "PROS/CONS" lists on the table
                    - A man examining floating, digitally scanned leaves and branches in a virtual reality museum

                    The text: {prompt}"""
        ],
        styles=[
            "Continuous lines very easy, very thin outline, clean and minimalist, black outline only, {prompt}",
            "Pixar style, dramatic, {prompt}",
            "Pixel style, dramatic, {prompt}",
        ],
    )
    grid_filename = f"data/grids/{datetime.now()}.png"
    os.makedirs("data/grids", exist_ok=True)
    plot_dataframe_of_images(df=df, output_filename=grid_filename)
    from lessmore.utils.system.open_in_os import open_in_os

    open_in_os(grid_filename)


if __name__ == "__main__":
    test()
