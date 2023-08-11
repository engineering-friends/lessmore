import openai


if __name__ == "__main__":
    print(
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "I want you to respond in a single emoji, one symbol. It should represent the following text: it's rainy outside today. ",
                },
            ],
        )
    )
    # sample answer: {"id":"chatcmpl-7mS5ErOokrcpg33WsJKrZ6rnhLazt","object":"chat.completion","created":1691782052,"model":"gpt-3.5-turbo-0613","choices":[{"index":0,"message":{"role":"assistant","content":"☔"},"finish_reason":"stop"}],"usage":{"prompt_tokens":44,"completion_tokens":2,"total_tokens":46}} # pragma: allowlist secret
