import os
import textwrap

from lessmore.utils.cache_on_disk import cache_on_disk
from openai import OpenAI


def ask(
    prompt: str,
    dedent: bool = True,
    open_ai_kwargs: dict = dict(model="gpt-4o"),
    cache: bool = True,
) -> str:
    # - Init function

    def _ask(
        prompt: str,
        dedent: bool,
        open_ai_kwargs: dict,
    ) -> str:
        return (
            OpenAI()
            .chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt.strip() if not dedent else textwrap.dedent(prompt).strip(),
                    },
                ],
                **open_ai_kwargs,
            )
            .choices[0]
            .message.content
        )

    # - Wrap cache if needed

    _ask = _ask if not cache else cache_on_disk(directory=os.path.join(os.path.dirname(__file__), "ask_cache/"))(_ask)

    # - Run

    return _ask(
        prompt=prompt,
        dedent=dedent,
        open_ai_kwargs=open_ai_kwargs,
    )


def test():
    assert ask("What is 2 + 2? Just the number") == "4"


if __name__ == "__main__":
    test()
