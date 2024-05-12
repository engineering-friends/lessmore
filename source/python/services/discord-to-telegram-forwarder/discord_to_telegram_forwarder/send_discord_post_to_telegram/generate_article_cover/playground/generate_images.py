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
    generate_image_kwargs: dict = {},
) -> pd.DataFrame:  # label, text, filename
    values = []

    # - Get combinations

    combinations = []
    for text_prompt_label, text_prompt in text_prompts_by_label.items():
        for image_prompt_label, image_prompt in image_prompts_by_label.items():
            for text in texts:
                combinations.append(
                    {
                        "text": text,
                        "text_prompt": text_prompt,
                        "text_prompt_label": text_prompt_label,
                        "image_prompt": image_prompt,
                        "image_prompt_label": image_prompt_label,
                    }
                )

    # - Run combinations

    for combination in tqdm.tqdm(combinations):
        generated_image = cache_on_disk()(generate_image)(
            text=combination["text"],
            text_prompt=combination["text_prompt"],
            image_prompt=combination["image_prompt"],
            **generate_image_kwargs,
        )
        values.append(
            [
                f"{combination['text_prompt_label']}--{combination['image_prompt_label']}",
                combination["text"],
                PIL.Image.open(PIL.Image.io.BytesIO(generated_image.image_contents)),
            ]
        )
    df = pd.DataFrame(values, columns=["label", "text", "image"])
    df = df.pivot(index="label", columns="text", values="image")
    return df


def test():
    df = generate_images(
        texts=read_file(filename="data/messages.json", reader=json.load)[:5],
        # texts=[
        #     """pixel art style, dramatic lighting: Cute Harry Potter, standing outside Hogwarts.""",
        #     # """From Finance to Marathons: A Man's Journey Through Personal and Professional Adventures""",
        # ],
        # texts=['AI Talks: Testing Alpha in Russia. A man tests the alpha version of a chat tool on his Russian profile.'],
        text_prompts_by_label={
            # "no_text_prompt": "",
            # "basic": "Describe in one small sentence, no more than 10 words: ",
            # "key_detail": "Extract key detail from the text in one sentence, no more than 10 words: ",
            # "movie_title": "If this text was a movie, what would be the title of the movie?: ",  # great!
            # "title_10plus_words": """If this text was a movie, what would be the title in 10+ words of the movie?
            #     Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)
            #     Just the title:"""
            # "auto": "Make a prompt for image generation. Use close-up, 50mm, f/1.2. Use no more than 20 words. Example:`Close up photography of coffee beans background roasted falling or flying on dark background. 50 mm f/1.2`. The prompt should describe the following text:"
            "title_10plus_words2": """                
                - There is an animated movie with a scene, that is described below. Describe the first shot of the scene. 
                - DO NOT INCLUDE any electronic devices with screens (e.g. phones, laptops, etc.)
                - It should be ONE shot, describing ONE scene. Choose any scene from the text.
                - It MUST have describe the text briefly, including it's core idea
                - Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)
                - Make it 15 words max
                
                
                Examples of other scenes: 
                - A man is standing in the middle of the desert, looking at the sky, happy
                - The night sky full of fireworks
                - Winter landscape with houses, trees and snow covered mountain background, a sky filled with snowflakes
                - A man finishing a grueling marathon race, crowd cheering, with a mountainous backdrop.
                - Man hands over documents at military registration desk, civilian officer reviews them, austere office setting.
                - Father and son discussing universities at home, papers with "PROS/CONS" lists on the table.
                - A man examining floating, digitally scanned leaves and branches in a virtual reality museum.
                
                The text: """
        },
        image_prompts_by_label={
            # 'roy': 'A painting by Roy Lichtenstein: '
            # 'no_image_prompt': '',
            # "low_details": "Pixel Art, LOW DETAILS:",
            # "zero_text": "Pixel Art, ZERO TEXT. People will be VERY upset if they find words in the image:",
            # "movie_poster": "pixar animated style:",
            "pixel": "pixel art style: ",
            "outline": "Continuous lines very easy, very thin outline, Clean and minimalist, black outline only:",
            "pixar": "pixar animated style: ",
            "close-up": "Close up photography, 50mm f/1.2: ",
            "roy": "Roy Lichtenstein: ",
            "bansky": "Banksy: ",
        },
    )
    grid_filename = f"data/grids/{datetime.now()}.png"
    os.makedirs("data/grids", exist_ok=True)
    plot_dataframe_of_images(df=df, output_filename=grid_filename)
    open_file_in_os(grid_filename)


"""
[
    "The night sky full of fireworks by Roy Lichtenstein",
    "An illustration of a blueberry sitting in a bar speaking to a bartender, saying ‘I just feel so blue today’ drinking a blue martini. The bartender is listening to him and pours more drink into his glass.",
    "Watercolor, christmas gift in blue, illustration, white background",
    "Design cute white tiger cub smiling, with tail, sticker, transparent background",
    "A snowy background Illustration, winter landscape with houses, trees and snow covered mountain background, A sky filled with snowflakes, large blank, 32k uhd",
    "Alaric’s Celestial Oration, in Jean Giraud moebius drawing style, in color",
    "Close up photography of coffee beans background roasted falling or flying on dark background. 50 mm f/1.2",
    "Beautiful Woman, portrait, sharp focus, 8k, masterpiece, RAW photo",
    "Happy kid with Christmas gifts. Coloring book page style for children. Continuous lines very easy, very thin outline, Clean and minimalist, black outline only",
    "South park character in front of angry Comic Book Designers. In a speech bubble saying ‘They Took Our Jobs!’"
]"""

if __name__ == "__main__":
    test()
