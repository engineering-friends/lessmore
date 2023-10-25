import emoji
import openai

from lessmore.utils.remove_duplicates_ordered import remove_duplicates_ordered


def request_emoji_representing_text_from_openai(text: str, limit: int = 3) -> str:
    """Returns emojis as a string (e.g. "👍")"""

    # - Get response text

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """Your role as an Emoji Interpreter Model is to read and understand the core sentiments, ideas, and themes of short texts. Your insights should then be translated into a sequence of five relevant emojis, capturing the essence of the text in a visual and succinct way. Your work will enable emoji-based communication and understanding of textual data.""",
            },
            {
                "role": "user",
                "content": """Механики навигации в рабочем флоу by Mark Lidenberg
        Хочу оптимизировать навигацию между разными сущностями при работе. Приложения, окна, вкладки, недавние, поиск по тексту, сессии, пины … - все вот это хочу разбить на рабочие механики и продумать, где что лучше как юзать""",
            },
            {"role": "assistant", "content": """🔍💡🗺️🚀🤔"""},
            {"role": "user", "content": f"### Text\n{text}"},
        ],
    )  # sample answer: {"id":"chatcmpl-7mS5ErOokrcpg33WsJKrZ6rnhLazt","object":"chat.completion","created":1691782052,"model":"gpt-3.5-turbo-0613","choices":[{"index":0,"message":{"role":"assistant","content":"☔"},"finish_reason":"stop"}],"usage":{"prompt_tokens":44,"completion_tokens":2,"total_tokens":46}} # pragma: allowlist secret
    response_text = response.choices[0].message.content

    # - Filter emojis

    emojis = [letter for letter in response_text if emoji.is_emoji(letter)]

    # - Remove duplicates

    emojis = remove_duplicates_ordered(emojis)

    # - Limit

    emojis = emojis[:limit]

    # - Return

    return "".join(emojis)


def test():
    print(
        request_emoji_representing_text_from_openai(
            "Yesterday I was walking in the street and I stepped in a puddle and my shoes got wet."
        )
    )


if __name__ == "__main__":
    test()
