import json
import os

from dataclasses import dataclass
from datetime import datetime

import requests

from box import Box
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.cache_on_disk import (
    cache_on_disk,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.generate_image_description import (
    generate_image_description,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.generate_article_cover.playground.plot_dataframe_of_images import (
    plot_dataframe_of_images,
)
from openai import OpenAI
from utils_ak.os import open_file_in_os


def generate_image(
    text: str,
    image_prompt: str,
    text_prompt: str = "",
    keep_original_prompt: bool = True,
) -> Box:
    # - Preprocess text if needed

    if text_prompt:
        text = cache_on_disk()(generate_image_description)(text=text, prompt=text_prompt)

    # - Set prompt prefix

    keep_prompt_prefix = (
        """I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"""
        if keep_original_prompt
        else ""
    )

    # - Create image

    response = OpenAI().images.generate(
        model="dall-e-3",
        prompt="\n".join([keep_prompt_prefix, image_prompt, text]),
        size="1024x1024",
        quality="standard",
        n=1,
    )

    # - Get image contents from url just as file contents

    return Box(
        image_contents=requests.get(response.data[0].url).content,
        revised_prompt=response.data[0].revised_prompt,
    )


def test():
    box = generate_image(
        text="""Escape the Draft: One Man's Elaborate Quest to Deregister from Military Service and Navigate the Maze of Bureaucracy""",
        image_prompt="pixel art :",
    )
    print(box.image_contents)


if __name__ == "__main__":
    test()
