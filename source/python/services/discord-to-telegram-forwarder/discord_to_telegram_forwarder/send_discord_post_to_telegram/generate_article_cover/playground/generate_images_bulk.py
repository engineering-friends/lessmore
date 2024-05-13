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
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.ask import ask
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.cache_on_disk import (
    cache_on_disk,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.generate_image import (
    generate_image,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.plot_dataframe_of_images import (
    plot_dataframe_of_images,
)
from retry import retry
from utils_ak.os import open_file_in_os


def generate_covers_bulk(
    texts: list[str],
    description_templates: [],
    style_templates: [],
) -> pd.DataFrame:  # label, text, filename
    values = []

    for text in tqdm.tqdm(texts):
        text_label = cache_on_disk()(ask)(prompt="Generate a two-word description for this text: {}".format(text))
        for description_template in description_templates:
            description_template_label = cache_on_disk()(ask)(
                prompt="Generate a two-word description for this description: {}".format(description_template)
            )

            description = cache_on_disk()(ask)(prompt=description_template.format(text=text))

            for style_template in style_templates:
                style_template_label = cache_on_disk()(ask)(
                    prompt="Generate a two-word description for this style: {}".format(style_template)
                )
                image_contents = cache_on_disk()(retry(tries=3, delay=1, exceptions=[AssertionError])(generate_image))(
                    prompt=style_template.format(description=description)
                )
                values.append(
                    {
                        "image": image_contents,
                        "text": text_label,
                        "style": f"{description_template_label}--{style_template_label}",
                    }
                )
    df = pd.DataFrame(values)
    df = df[["text", "style", "image"]]
    df = df.pivot(index="style", columns="text", values="image")
    return df


def test():
    df = generate_covers_bulk(
        texts=[
            "AI Talks, Testing Alpha in Russia. A man tests the alpha version of a chat tool on his Russian profile."
        ],
        description_templates=[
            "",
            # "Describe in one small sentence, no more than 10 words: {text}",
            # "Extract key detail from the text in one sentence, no more than 10 words: {text}",
            # "If this text was a movie, what would be the title of the movie?: {text}",
            # "If this text was a movie, what would be the title in 10+ words of the movie?\n Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)\n Just the title: {text}",
            # '- There is an animated movie with a scene, that is described below. Describe the first shot of the scene\n - EXCLUDE all electronic devices with screens (e.g. phones, laptops, etc.)\n - It should be ONE shot, describing ONE scene. Choose any scene from the text\n - It MUST have describe the text briefly, including it\'s core idea\n - Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)\n                - Make it 15 words max\n\n                Examples of other scenes:\n                - A man is standing in the middle of the desert, looking at the sky, happy\n                - The night sky full of fireworks\n                - Winter landscape with houses, trees and snow covered mountain background, a sky filled with snowflakes\n                - A man finishing a grueling marathon race, crowd cheering, with a mountainous backdrop\n                - Man hands over documents at military registration desk, civilian officer reviews them, austere office setting\n                - Father and son discussing universities at home, papers with "PROS/CONS" lists on the table\n                - A man examining floating, digitally scanned leaves and branches in a virtual reality museum\n\n The text: {text}',
        ],
        style_templates="A Pixar-style shot from the film, {description}",
    )
    grid_filename = f"data/grids/{datetime.now()}.png"
    os.makedirs("data/grids", exist_ok=True)
    plot_dataframe_of_images(df=df, output_filename=grid_filename)
    open_file_in_os(grid_filename)


if __name__ == "__main__":
    test()
