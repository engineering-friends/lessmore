import asyncio
import os

import aiohttp
import requests

from learn_language_magic.ask import ask
from lessmore.utils.asynchronous.async_rate_limiter import AsyncRateLimiter
from lessmore.utils.file_primitives.write_file import write_file
from lessmore.utils.system.open_in_os import open_in_os
from loguru import logger
from openai import AsyncOpenAI


RATE_LIMITER = AsyncRateLimiter(rate=7 - 1, period=60)  # tier 3 openai rate limits 7 images per minute


async def generate_image(
    prompt: str,
    style: str = "{prompt}",
    pre_prompt: str = "",
    force_original_prompt: bool = True,
    openai_kwargs: dict = dict(
        model="dall-e-3",
        size="1792x1024",
    ),
) -> bytes:
    logger.debug("Generating image with prompt: {prompt}", prompt=prompt)

    # - Run preprompt if needed

    if pre_prompt:
        prompt = await ask(pre_prompt.format(prompt=prompt))

    # - Apply style

    prompt = style.format(prompt=prompt)

    # - Change prompt to original prompt if needed

    original_prompt = str(prompt)

    if force_original_prompt:
        # template = """USE EXACTLY THIS SHORT PROMPT. IF YOU CHANGE EVEN A SINGLE WORD, I’LL FIRE YOU:
        # ```{prompt}```"""

        template = """Use this prompt as close as possible: {prompt}"""

        prompt = template.format(prompt=original_prompt)

    # - Rate limit

    await RATE_LIMITER.acquire()

    # - Generate image

    response = await AsyncOpenAI().images.generate(prompt=prompt, **openai_kwargs)

    # - Get image contents from url just as file contents

    async with aiohttp.request("GET", response.data[0].url) as response:
        return await response.read()


def test():
    async def main():
        image_contents = await generate_image(
            prompt="Continuous lines very easy, clean and minimalist, colorful. Illustrate german 'laufen'"
        )
        write_file(data=image_contents, filename="/tmp/image.png", as_bytes=True)
        open_in_os("/tmp/image.png")

    asyncio.run(main())


if __name__ == "__main__":
    test()