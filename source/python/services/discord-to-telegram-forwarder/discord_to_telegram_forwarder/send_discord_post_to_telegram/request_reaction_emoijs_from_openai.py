import os
import time

import emoji

from openai import OpenAI

from lessmore.utils.functional.skip_duplicates import skip_duplicates


REACTION_EMOJIS = [
    "🔥",
    "👍",
    "✍️",
    "😁",
    "👀",
    "😢",
    "👾",
    "❤️",
    "🤝",
    "🎉",
    "🙏",
    "💯",
    "🥰",
    "👏",
    # "🤔",
    "🤯",
    "😱",
    "🤬",
    "🤩",
    "🕊️",
    "🥴",
    "😍",
    "🐳",
    "🌚",
    "🌭",
    "🤣",
    "⚡",
    "🍌",
    "🏆",
    "💔",
    "🤨",
    "🍓",
    "💋",
    "😈",
    "😴",
    "🙈",
    "😇",
    "🤗",
    "🫡",
    "🎄",
    "☃️",
    "🆒",
    "🦄",
    "🤷",
]


def request_reaction_emojis_from_openai(text: str, limit: int = 3) -> str:
    """Returns emojis as a string (e.g. "👍")"""

    # - Init client

    client = OpenAI()

    # - Get response text

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """
                Your role as an Emoji Reactor is to react to the text with emojis.
                Focus on the core ideas and sentiments of the text that make it stand out. 
                
                Use ONLY emojis from the list below:
                🔥 👍 ✍️ 😁 👀 😢 👾 ❤️ 🤝 🎉 🙏 💯 🥰 👏 🤯 😱 🤬 🤩 🕊️ 🥴 😍 🐳 🌚 🌭 🤣 ⚡ 🍌 🏆 💔 🤨 🍓 💋 😈 😴 🙈 😇 🤗 🫡 🎄 ☃️ 🆒 🦄 🤷
                """,
            },
            {
                "role": "user",
                "content": """⏳ Не вывожу текучку, пожалуйста помогите разгрести. by Petr Lavrov (https://www.notion.so/Petr-Lavrov-578c90b40fb642809540b6c8794c81dd)

Побудьте моими руками, головой, координатором или просто рядом постойте. Если у вас есть время / силы / желание.

Позвоните / заставьте / сделайте за меня

Хочу по каждой задаче - либо сделать, либо принять решение не делать / отложить, либо как-то организовать чтобы оно само / за меня / без меня сделалось.

Конкретно, что уже долго висит:
- разузнать продлят ли нам пермит если выдавал Цюрих а работодатель в Цуге
- неотвеченные письма связанные со сменой работы. Страховка, пенсия
- собрать и отправить документы по налогам, дедлайн когда-то в сентябре? Или в августе?
""",
            },
            {
                "role": "assistant",
                "content": """🤯😱🤷""",
            },
            {
                "role": "user",
                "content": f"### Text\n{text}",
            },
        ],
    )  # sample answer: {"id":"chatcmpl-7mS5ErOokrcpg33WsJKrZ6rnhLazt","object":"chat.completion","created":1691782052,"model":"gpt-3.5-turbo-0613","choices":[{"index":0,"message":{"role":"assistant","content":"☔"},"finish_reason":"stop"}],"usage":{"prompt_tokens":44,"completion_tokens":2,"total_tokens":46}} # pragma: allowlist secret
    response_text = response.choices[0].message.content

    # - Filter emojis

    emojis = [letter for letter in response_text if emoji.is_emoji(letter)]

    # - Remove duplicates

    emojis = list(skip_duplicates(emojis))

    # - Filter non-reaction emojis

    emojis = [_emoji for _emoji in emojis if _emoji in REACTION_EMOJIS]

    if not emojis:
        emojis = ["👀"]

    # - Return the first one

    return "".join(emojis[:limit])


def test():
    for text in [
        """к слову про AI Search в своих файлах by Petr Lavrov

https://www.theverge.com/2023/6/21/23767248/dropbox-ai-dash-universal-search""",
        """А все знают, что значит вот это число в форварде поста?""",
        """Попробовал DALLE-3 (через Bing), очень понравилось by Petr Lavrov

https://www.bing.com/images/create/
с Midjourney гораздо сложнее было сгенерить то что хочется
""",
        """Илья, а мне зашел birthdaycountbot :) Создает доброе ощущение sense of urgency by Mark Lidenberg

Пока оставлю :) 

https://t.me/birthdaycountbot

Илья (Ilya)""",
        """Кто делал себе вторую личность? Как правильно подготовить себя к заляганию на дно? by Georgy Gorbachev

Я собрал определённый набор предметов для второй иностранной личности, однако как будто этого недостаточно. Хочу поделиться и проконсультироваться)))

Также делаю себе advanved VPN cluster своими руками для впна как в РФ так и во вне для себя и семьи под прикрытием игрового сервиса, пробивающий будущую блокировку дипиайями большинство существующих VPN-протоколов. Обсудил бы это если останется время)""",
        """ Хочу обсудить проблемы  недостатки и классные фичи приложений для изучения языков by Илья (Ilya)

Разрабатываю прототип мобильного приложения, являющегося лучшей версией anki и хочу услышать об опыте взаимодействия с приложениями для изучения языков. Что понравилось, и чего не хватало""",
    ]:
        print(text[:10], request_reaction_emojis_from_openai(text, limit=3))
        time.sleep(1)


if __name__ == "__main__":
    test()
