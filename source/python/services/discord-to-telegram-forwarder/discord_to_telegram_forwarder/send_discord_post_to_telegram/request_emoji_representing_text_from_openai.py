import openai
import random
import re


PROMPT_TEMPLATE_SIMPLE = (
    "I want you to respond in a single emoji. Only ONE symbol. It should represent the following text: {text}"
)
PROMPT_TEMPLATE_COMPLEX = "### Text\n{text}"


def filter_and_limit_emojis(s, linit=5):
    emojis = re.findall(r"[^\w\s,]", s)
    emojis = [e for e in emojis if ord(e) > 255]  # Crude way, use the emoji package if you want to be robust.
    return "".join(emojis[:limit])


def request_emoji_representing_text_from_openai(text: str) -> str:
    """Returns emoji as a string (e.g. "👍"). Or several."""

    role_message = """Your role as an Emoji Interpreter Model is to read and understand the core sentiments, ideas, and themes of short texts. Your insights should then be translated into a sequence of five relevant emojis, capturing the essence of the text in a visual and succinct way. Your work will enable emoji-based communication and understanding of textual data."""
    warmup_messages = [
        {
            "role": "user",
            "content": """Механики навигации в рабочем флоу by Mark Lidenberg
Хочу оптимизировать навигацию между разными сущностями при работе. Приложения, окна, вкладки, недавние, поиск по тексту, сессии, пины … - все вот это хочу разбить на рабочие механики и продумать, где что лучше как юзать""",
        },
        {"role": "assistant", "content": """🔍💡🗺️🚀🤔"""},
    ]
    messages_rich = [
        {
            "role": "system",
            "content": role_message,
        },
        *warmup_messages,
        {
            "role": "user",
            "content": PROMPT_TEMPLATE_COMPLEX.format(text=text),
        },
    ]

    messages_simple = (
        [
            {
                "role": "user",
                "content": PROMPT_TEMPLATE_SIMPLE.format(text=text),
            },
        ],
    )

    messages = random.choices([messages_simple, messages_rich], weights=[0.4, 0.6], k=1)[0]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )  # sample answer: {"id":"chatcmpl-7mS5ErOokrcpg33WsJKrZ6rnhLazt","object":"chat.completion","created":1691782052,"model":"gpt-3.5-turbo-0613","choices":[{"index":0,"message":{"role":"assistant","content":"☔"},"finish_reason":"stop"}],"usage":{"prompt_tokens":44,"completion_tokens":2,"total_tokens":46}} # pragma: allowlist secret

    return filter_and_limit_emojis(response.choices[0].message.content)


def test():
    print(filter_and_limit_emojis("Тестим 😄🌟🌈🐱🐶🐼🌺"), limit=5)  # Output: 😄🌟🌈🐱🐶
    print(
        request_emoji_representing_text_from_openai(
            "Yesterday I was walking in the street and I stepped in a puddle and my shoes got wet."
        )
    )


if __name__ == "__main__":
    test()
