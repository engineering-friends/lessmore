import math
import random
import time

import emoji
import openai

from discord_to_telegram_forwarder.config.config import EmojiPack
from pytest import mark

from lessmore.utils.remove_duplicates_ordered import remove_duplicates_ordered


# Signature Mark Emojis
MINIMAL_EMOJIS = """👾🕊️🤍👍👎👌🙂🙃😢☹️"""


CORE_EMOJIS = (
    # faces
    """👨😀😕😃😄😁😆😅🤣😂🙂🙃😉😊😗😙😚😋😛😜😝🤗🤔🤨😐😑😶😏😒🙄😬🤥😌😔😪🤤🥴😕😟🙁☹️😮😯😲😳😦😧😖😣😞😓😩😫😠"""
    +
    # hands
    """👍👎👌👏👋🤚🖐✋🖖👌🤏✌️🤞🤟🤘👈👉👆👇☝️🤛🤜👏👐🤲🙏🤝👐🫱🫲"""
    +
    # signs
    """🤷♂♀🤦🔍🔎❓❗️❔❕💡"""
)

emoji_packs_map = {
    EmojiPack.MINIMAL: MINIMAL_EMOJIS + CORE_EMOJIS,
    EmojiPack.CORE: CORE_EMOJIS + MINIMAL_EMOJIS,
    EmojiPack.ALL: "",
}


def request_emoji_representing_text_from_openai(
    text: str, limit: int = 1, emoji_pack: EmojiPack = EmojiPack.CORE
) -> str:
    """Returns emojis as a string (e.g. "👍")"""

    # - Convert emoji_pack to Enum

    emoji_pack = EmojiPack(emoji_pack)

    # - Get response text
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": """
                Your role as an Emoji Interpreter Model is to read and understand the core sentiments, ideas, and themes of short texts. 
                Your insights should then be translated into one to five emojis, each of which captures the essence of the text in a visual and succinct way. 
                Your work will enable emoji-based communication and understanding of textual data.
                Focus on the core ideas and sentiments of the text that make it stand out. 
                """,
            },
            {
                "role": "user",
                "content": """Кто делал себе вторую личность? Как правильно подготовить себя к заляганию на дно? by Georgy Gorbachev

Я собрал определённый набор предметов для второй иностранной личности, однако как будто этого недостаточно. Хочу поделиться и проконсультироваться)))

Также делаю себе advanved VPN cluster своими руками для впна как в РФ так и во вне для себя и семьи под прикрытием игрового сервиса, пробивающий будущую блокировку дипиайями большинство существующих VPN-протоколов. Обсудил бы это если останется время)""",
            },
            {
                "role": "assistant",
                "content": """🎭💼🕵🌐🔒""",
            },
            {
                "role": "user",
                "content": """I went to the cinema and saw a movie about
            Strange yellow creatures with one or two eyes. 
            I think they are called minions. 
            They are very funny and cute. I like them. I want to have one as a pet. 
            I think they are very smart and can do a lot of things.
            After that I went to the park and saw a lot of people. 
            I thought: They must be like minions. 
            They wear the same clothes and have the same hair.
            They wait for the bus and talk to each other.
            """,
            },
            {"role": "assistant", "content": """🎥🍿👶🦮💇"""},
            {
                "role": "user",
                "content": """Завтрак у Тиффани!""",
            },
            {
                "role": "assistant",
                "content": """👒""",
            },
            {
                "role": "user",
                "content": """А я сегодня посмотрел завтрак у Тиффани!""",
            },
            {
                "role": "assistant",
                "content": """🍳🥐🥂👩🏻‍🦰🐈""",
            },
            {
                "role": "user",
                "content": """Ходили в зоопарк смотреть на макак""",
            },
            {
                "role": "assistant",
                "content": """🐒""",
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

    # - Move ~~awesome~~ boring emojis to the end

    preferred_emojis = emoji_packs_map[emoji_pack]
    emojis = list(sorted(emojis, key=lambda emoji: emoji in preferred_emojis))

    # - Remove duplicates

    emojis = remove_duplicates_ordered(emojis)

    # - Return the first one

    return "".join(emojis[:limit])


test_texts = [
    """Peterson Lecture Series: По поводу того, что с ютуба удалили все плейлисты с Гарвардскими курсами лекций Питерсона - но все оригинальные видео до сих пор остались на канале, я их выгрузил

Кстати, попробовал по дороге Барда с youtube access plugin - полное говно, не справился) 

Зато вот из Youtube Data API все досталось""",
    """Расскажите как и что вы автоматизируете в личной жизни? Телеграм / Slack боты
Apple Shortcuts / automations (реально используемые регулярно)
cron jobs? Notion Automations?
Zapier / Move?

Рассказать про мои?)""",
    """Как найти в хроме вкладку на которой играет видео / звук. Cmd + Shift + A - поиск по всем вкладкам.
Вкладка с аудио (из любого окна) будет вверху
""",
    """Возвращаясь к теме закаливания""",
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
]


@mark.parametrize("max_count, emoji_pack", list(zip([5, 3, 1], ["all", "core", "minimal"])))
def test_parametrized(max_count, emoji_pack):
    for text in test_texts:
        limit = max_count - math.isqrt(random.randint(0, max_count * max_count - 1))
        emoji = request_emoji_representing_text_from_openai(text, limit=limit, emoji_pack=emoji_pack)
        print(f"{text[:20]}... -> {emoji} (limit={limit}, pack={emoji_pack})")
        time.sleep(0.5)


if __name__ == "__main__":
    test_parametrized()
