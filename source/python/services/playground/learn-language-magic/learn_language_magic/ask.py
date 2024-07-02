import json
import os
import textwrap

from lessmore.utils.cache_on_disk import cache_on_disk
from openai import OpenAI
from openai.types.chat import completion_create_params


def ask(
    prompt: str,
    dedent: bool = True,
    open_ai_kwargs: dict = dict(model="gpt-4o"),
    cache: bool = True,
    json_template: str = "",
) -> str:
    # - Copy open_ai_kwargs to avoid side effects

    open_ai_kwargs = open_ai_kwargs.copy()

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

    # - Process JSON

    if json_template:
        open_ai_kwargs["response_format"] = completion_create_params.ResponseFormat(type="json_object")
        prompt += f"\n Answer in JSON. Template: \n```{json_template}\n```"

        return json.loads(
            _ask(
                prompt=prompt,
                dedent=dedent,
                open_ai_kwargs=open_ai_kwargs,
            )
        )["answer"]

    # - Run function

    return _ask(
        prompt=prompt,
        dedent=dedent,
        open_ai_kwargs=open_ai_kwargs,
    )


def test():
    assert ask("What is 2 + 2? Just the number") == "4"
    assert ask("What is the capital of France?", json_template='{"answer": "London"}') == "Paris"


if __name__ == "__main__":
    test()
