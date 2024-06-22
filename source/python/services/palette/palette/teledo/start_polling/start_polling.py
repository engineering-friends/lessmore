import asyncio

from typing import Callable, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from palette.deps import Deps
from palette.teledo.archive.thread_handler import thread_handler
from palette.teledo.elements.lib.button_element import ButtonElement
from palette.teledo.start_polling.global_callback_query_handler import global_callback_query_handler
from palette.teledo.start_polling.global_message_handler import get_global_message_handler


async def start_polling(
    bot: Bot | str,
    command_starters: dict[str, Callable] = {},  # {'/start': def f(message: Message): ...}
    message_starter: Optional[Callable] = None,  # def f(message: Message): ...
    default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
) -> None:
    # - Init dispatcher

    dp = Dispatcher()

    # - Register handlers

    dp.callback_query.register(global_callback_query_handler)
    dp.message.register(
        get_global_message_handler(
            command_starters=command_starters,
            message_starter=message_starter,
        )
    )

    # - Init bot from token if needed

    if isinstance(bot, str):
        bot = Bot(
            token=bot,
            default=default_bot_properties,
        )

    # - Start polling

    await dp.start_polling(bot)


def test() -> None:
    asyncio.run(
        start_polling(
            bot=Bot(
                token=Deps.load().config.telegram_bot_token,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            )
        )
    )


if __name__ == "__main__":
    test()
