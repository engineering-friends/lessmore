import json
import os
import random

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


RANDOMIZERS = [
    "ancient",
    "mystical",
    "luminous",
    "enigmatic",
    "whimsical",
    "tranquil",
    "opulent",
    "rustic",
    "vivid",
    "ethereal",
    "grotesque",
    "serene",
    "majestic",
    "quaint",
    "baroque",
    "minimalist",
    "ornate",
    "bleak",
    "surreal",
    "vibrant",
    "dystopian",
    "idyllic",
    "gloomy",
    "futuristic",
    "timeless",
    "decadent",
    "eerie",
    "splendid",
    "rugged",
    "buoyant",
    "melancholic",
    "pristine",
    "chaotic",
    "cozy",
    "stark",
    "lavish",
    "haunting",
    "abstract",
    "radiant",
    "murky",
    "gleaming",
    "forgotten",
    "stunning",
    "bizarre",
    "crisp",
    "dilapidated",
    "lush",
    "turbulent",
]


def generate_image(
    text: str,
    image_prompt: str,
    text_prompt: str = "",
    keep_original_prompt: bool = True,
    size: str = "1792x1024",
    quality: str = "standard",
    style: str = "vivid",
    model: str = "dall-e-3",
) -> Box:
    # - Preprocess text if needed

    for attempt in range(5):
        if text_prompt:
            text = cache_on_disk(reset=attempt != 0)(generate_image_description)(
                text=text,
                prompt="\n".join(["" if attempt == 0 else random.choice(RANDOMIZERS), text_prompt]),
            )
            print()
            print(text)
            print()

        # - Set prompt prefix

        keep_prompt_prefix = (
            """I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:"""
            if keep_original_prompt
            else ""
        )

        # - Create image

        try:
            response = OpenAI().images.generate(
                model=model,
                prompt="\n".join([keep_prompt_prefix, image_prompt, text]),
                size=size,
                quality=quality,
                style=style,
                n=1,
            )

        except Exception as e:
            if "content_policy_violation" in str(e):
                print("Content policy violation, trying again, attempt", attempt)
                continue
            else:
                raise e

        break

    # - Get image contents from url just as file contents

    return Box(
        image_contents=requests.get(response.data[0].url).content,
        revised_prompt=response.data[0].revised_prompt,
    )


def test():
    box = generate_image(
        text="""#session_requests
💬 **Новые целевые запросы на коворкинг** by Petr Lavrov

Хочу посидеть поковырять виспер бота
Вероятно ~alexeykudrinsky 

Хочу посидеть поковырять GPT Assistant (телеграм бот чтобы он тебе в календаре умел события рисовать и напоминалки/джобы скедулить)
Вероятно Konstantin Ershov, или Mitya Shabat если интересно
Хочу на базе собранных данных о локациях сделать сайт 146 школы с картой, залогином, админкой, базой и возможностью вносить / редактировать данные
Вероятно ~palych65 

Хочу настроить себе data feed личных данных - письма, календарь, браузерные букмарки, (история Ютуба?), Слак, дискорд, чатики в телеге
Notion? 
- хочу попробовать для этого prefect.hq или тупо n8n
Вероятно Mikhail Vodolagin, или Daniel Lytkin 

Хочу писать тулзы продуктивности на базе GPT
Вероятно Mark Lidenberg 
Кстати у Alexander Votyakov есть интерес к habit tracker, можем обсудить это делать вместе или отдельно

[→ к посту](https://discord.com/channels/1106702799938519211/1223037035460427949/1223037035460427949) / [→ к посту для ](https://tinyurl.com/2bbmjeut) (+19)""",
        image_prompt="pixel art :",
        text_prompt="""If this text was a movie, what would be the title in 10+ words of the movie?
                Skip any people names, use abstract forms (e.g. Petr Lavrov -> a man). Keep intact other names (e.g. Apple, Russia, ChatGPT, ...)  
                Just the title:""",
    )

    # save image to file

    with open("/tmp/image.png", "wb") as f:
        f.write(box.image_contents)
    open_file_in_os("/tmp/image.png")


if __name__ == "__main__":
    test()
