import json
import os
import textwrap

from typing import Union

from learn_language_magic.rate_limiter import RateLimiter
from lessmore.utils.cache_on_disk import cache_on_disk
from openai import AsyncOpenAI
from openai.types.chat import completion_create_params


RATE_LIMITER = RateLimiter(rate=5000 - 500, period=60)  # tier 3 openai rate limits 5000RPM, subtract 10% to be safe


async def ask(
    prompt: str,
    dedent: bool = True,
    open_ai_kwargs: dict = dict(model="gpt-4o"),
    cache: bool = True,
    template: str | dict = "",
) -> str:
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

        return (
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

    # - Wrap cache if needed

    _ask = _ask if not cache else cache_on_disk(directory=os.path.join(os.path.dirname(__file__), "ask_cache/"))(_ask)

    # - Process JSON

    if template:
        open_ai_kwargs["response_format"] = completion_create_params.ResponseFormat(type="json_object")
        prompt += f"""\n Answer in JSON. Template: \n```{json.dumps({"answer": template})}\n```"""

        return json.loads(
            await _ask(
                prompt=prompt,
                dedent=dedent,
                open_ai_kwargs=open_ai_kwargs,
            )
        )["answer"]

    # - Run function

    return await _ask(
        prompt=prompt,
        dedent=dedent,
        open_ai_kwargs=open_ai_kwargs,
    )


def test():
    assert ask("What is 2 + 2? Just the number") == "4"
    assert ask("What is the capital of France?", template='{"answer": "London"}') == "Paris"


if __name__ == "__main__":
    test()
