from openai import OpenAI


def ask(
    prompt: str,
    open_ai_kwargs: dict = dict(model="gpt-4o"),
) -> str:
    return (
        OpenAI()
        .chat.completions.create(
            messages=[
                {"role": "user", "content": prompt.strip()},
            ],
            **open_ai_kwargs
        )
        .choices[0]
        .message.content
    )


def test():
    assert ask("What is 2 + 2? Just the number") == "4"


if __name__ == "__main__":
    test()
