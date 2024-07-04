import asyncio
import json
import os
import textwrap

from lessmore.utils.asynchronous.async_rate_limiter import AsyncRateLimiter
from lessmore.utils.cache_on_disk import cache_on_disk
from loguru import logger
from openai import AsyncOpenAI
from openai.types.chat import completion_create_params


RATE_LIMITER = AsyncRateLimiter(
    rate=5000 - 500, period=60
)  # tier 3 openai rate limits 5000RPM, subtract 10% to be safe


async def ask(
    prompt: str,
    dedent: bool = True,
    open_ai_kwargs: dict = dict(model="gpt-4o"),
    cache: bool = True,
    example: str | dict = "",
) -> str | dict | list:
    # - Copy open_ai_kwargs to avoid side effects

    open_ai_kwargs = open_ai_kwargs.copy()

    # - Init function

    async def _ask(
        prompt: str,
        dedent: bool,
        open_ai_kwargs: dict,
    ) -> str:
        # - Acquire rate limiter

        await RATE_LIMITER.acquire()

        # - Ask

        logger.debug("Making request to OpenAI", prompt=prompt)

        result = (
            (
                await AsyncOpenAI().chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt.strip() if not dedent else textwrap.dedent(prompt).strip(),
                        },
                    ],
                    **open_ai_kwargs,
                )
            )
            .choices[0]
            .message.content
        )

        # - Validate json

        if example:
            assert "response" in json.loads(result), f"Expected JSON with key 'response', got: {result}"

        # - Return

        return result

    # - Wrap cache if needed

    _ask = (
        _ask
        if not cache
        else cache_on_disk(directory=os.path.join(os.path.dirname(__file__), "data/dynamic/.ask_cache/"))(_ask)
    )

    # - Process JSON

    if example:
        open_ai_kwargs["response_format"] = completion_create_params.ResponseFormat(type="json_object")
        prompt += f"""\n Answer in JSON with root key `response`. Example: \n```{json.dumps({"response": example}, ensure_ascii=False)}\n```"""

        return json.loads(
            await _ask(
                prompt=prompt,
                dedent=dedent,
                open_ai_kwargs=open_ai_kwargs,
            )
        )["response"]

    # - Run function

    return await _ask(
        prompt=prompt,
        dedent=dedent,
        open_ai_kwargs=open_ai_kwargs,
    )


def test():
    async def main():
        assert await ask("What is 2 + 2? Just the number") == "4"
        assert await ask("What is the capital of France?", example="London") == "Paris"

    asyncio.run(main())


if __name__ == "__main__":
    test()
