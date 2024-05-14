from typing import Callable

import requests

from box import Box
from discord_to_telegram_forwarder.send_discord_post_to_telegram.ai.ask import ask
from openai import OpenAI


def generate_image(
    prompt: str,
    style: str = "{prompt}",
    pre_prompt: str = "",
    force_original_prompt: bool = True,
    openai_kwargs: dict = dict(
        model="dall-e-3",
        size="1792x1024",
    ),
) -> Box:
    # - Run preprompt if needed

    if pre_prompt:
        prompt = ask(pre_prompt.format(prompt=prompt))

    # - Apply style

    prompt = style.format(prompt=prompt)

    # - Change prompt to original prompt if needed

    original_prompt = str(prompt)

    if force_original_prompt:
        # template = """USE EXACTLY THIS SHORT PROMPT. IF YOU CHANGE EVEN A SINGLE WORD, I’LL FIRE YOU:
        # ```{prompt}```"""

        template = """Use this prompt as close as possible: {prompt}"""

        prompt = template.format(prompt=original_prompt)

    # - Generate image

    response = OpenAI().images.generate(prompt=prompt, **openai_kwargs)

    # - Get image contents from url just as file contents

    return requests.get(response.data[0].url).content


def test():
    image_contents = generate_image(
        prompt="Continuous lines very easy, very thin outline, clean and minimalist, black outline only, a cat with a beard."
    )
    with open("/tmp/image.png", "wb") as f:
        f.write(image_contents)
    from utils_ak.os import open_file_in_os

    open_file_in_os("/tmp/image.png")


if __name__ == "__main__":
    test()
