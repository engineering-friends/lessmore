import openai


PROMPT_TEMPLATE = (
    "I want you to respond in a single emoji. Only ONE symbol. It should represent the following text: {text}"
)


def get_emoji_from_text(text):
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
    print(get_emoji_from_text("channel_name title body"))


if __name__ == "__main__":
    test()
