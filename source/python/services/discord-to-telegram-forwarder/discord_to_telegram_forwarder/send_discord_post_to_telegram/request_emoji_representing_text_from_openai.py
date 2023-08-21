import openai


PROMPT_TEMPLATE = (
    "I want you to respond in a single emoji. Only ONE symbol. It should represent the following text: {text}"
)


def request_emoji_representing_text_from_openai(text: str) -> str:
    """Returns emoji as a string (e.g. "👍")"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(text=text),
            },
        ],
    )  # sample answer: {"id":"chatcmpl-7mS5ErOokrcpg33WsJKrZ6rnhLazt","object":"chat.completion","created":1691782052,"model":"gpt-3.5-turbo-0613","choices":[{"index":0,"message":{"role":"assistant","content":"☔"},"finish_reason":"stop"}],"usage":{"prompt_tokens":44,"completion_tokens":2,"total_tokens":46}} # pragma: allowlist secret

    return response.choices[0].message.content


def test():
    print(
        request_emoji_representing_text_from_openai(
            "Yesterday I was walking in the street and I stepped in a puddle and my shoes got wet."
        )
    )


if __name__ == "__main__":
    test()
