import asyncio

from typing import Callable, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, Message

from palette.deps import Deps
from palette.teletalk.crowd.crowd import crowd
from palette.teletalk.crowd.talk import Talk
from palette.teletalk.start_polling.global_callback_query_handler import global_callback_query_handler
from palette.teletalk.start_polling.global_message_handler import get_global_message_handler


async def start_polling(
    bot: Bot | str,
    command_starters: dict[str, Callable] = {},  # {'/start': def f(message: Message): ...}
    message_starter: Optional[Callable] = None,  # def f(message: Message): ...
    default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
    commands: list[BotCommand] = [],
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

    # - Set commands for bot

    await bot.set_my_commands(commands=commands)

    # - Start polling

    await dp.start_polling(bot)


def test() -> None:
    async def message_starter(message: Message, talk: Talk) -> None:
        await message.answer("Message received!")

    async def command_starter(message: Message, talk: Talk) -> None:
        await message.answer("Command received!")

    asyncio.run(
        start_polling(
            message_starter=message_starter,
            command_starters={"/start": command_starter, "/new": command_starter},
            bot=Deps.load().config.telegram_bot_token,
        )
    )


if __name__ == "__main__":
    test()
