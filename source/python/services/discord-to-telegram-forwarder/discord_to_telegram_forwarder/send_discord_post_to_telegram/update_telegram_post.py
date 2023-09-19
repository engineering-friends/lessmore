import asyncio
import re

from typing import Callable, Optional, Sequence, Union

import discord
import emoji as emoji_lib
import pyperclip

from box import Box
from discord_to_telegram_forwarder.send_discord_post_to_telegram.format_message import format_message
from discord_to_telegram_forwarder.send_discord_post_to_telegram.get_shortened_url_from_tiny_url import (
    get_shortened_url_from_tiny_url,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.is_discord_channel_private import (
    is_discord_channel_private,
)
from discord_to_telegram_forwarder.send_discord_post_to_telegram.request_emoji_representing_text_from_openai import (
    request_emoji_representing_text_from_openai,
)
from discord_to_telegram_forwarder.telegram_client import telegram_client
from frozendict import frozendict
from loguru import logger
from pymaybe import maybe


async def update_telegram_post(message: discord.Message) -> None:
    # - Find telegram message

    telegram_messages = [
        # message async for message in telegram_client.iter_messages(-1001829309947, search=message.channel.name)
        message
        async for message in telegram_client.iter_messages("@marklidenberg", search=message.channel.name)
    ]

    if not telegram_messages:
        logger.warning(f"Telegram message not found for discord message", content=message.content)
        return

    content = telegram_messages[0].text

    comments_count = message.channel.message_count

    if re.search(r"\(\+?\d+\)$", content):
        content = re.sub(r"\(\+?\d+\)$", f"({'+' if comments_count else ''}{comments_count})", content)
    else:
        # strip new lines at the end

        content = content.rstrip()
        content = content + f" ({'+' if comments_count else ''}{comments_count})"

    await telegram_client.edit_message(
        entity=telegram_messages[0],
        message=content,
        parse_mode="md",
        link_preview=False,
        # file=filename_urls or None,
    )


def test():
    content = '''
    #software_engineering
🤔 Хочу способ нормально организовывать ?тестовые ?текстовые классы by Mikhail Vodolagin

Минимальный рек это чтобы куски смысла были collapsable в нормальных IDE
Типа у меня есть много вот такого, но с сильно более жырной тушкой. И мне больно с ними делать вообще всё. Читать, менять, проматывать. Хочу идеи как лучше

    class TestCommon(TestBase):
        role_message = """
                You act strange. 
                """
        prompt_parts = [
            """
            ### Input
            {user_prompt}
            """
            """
            ### Data
            {mock_data}
            """,
        ]

    class Test_0(TestCommon):
        role_message = """
            You act as a seal. But the others should think that you are an alien.       
            """

    class Test_1(TestCommon):
        prompt_parts = [
            """
            You act as a seal. But the others should think that you are an alien.
            """,
            *TestCommon.prompt_parts[:],
        ]

classes_to_test = [cls for cls in TestCommon.subclasses()]

→ к посту / → к посту для 
    '''
    comments_count = 10
    if re.search(r"\(\+?\d+\)$", content):
        content = re.sub(r"\(\+?\d+\)$", f"({'+' if comments_count else ''}{comments_count})", content)
    else:
        # strip new lines at the end

        content = content.rstrip()
        content = content + f" ({'+' if comments_count else ''}{comments_count})"
    print(content)
    # print(re.sub(r"\(\+?\d+\)$", 'foo', content, flags=re.MULTILINE))


if __name__ == "__main__":
    test()
