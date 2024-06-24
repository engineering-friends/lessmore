import asyncio

from typing import Callable, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, Message

from palette.deps import Deps
from palette.teletalk.crowd.crowd import Crowd
from palette.teletalk.crowd.talk.talk import Talk


async def start_polling(
    bot: Bot | str,
    command_starters: dict[str, Callable] = {},  # {'/start': def f(message: Message): ...}
    message_starter: Optional[Callable] = None,  # def f(message: Message): ...
    default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
    commands: Optional[list[BotCommand]] = None,  # description of commands
    on_early_response: Optional[Callable] = None,  # todo later: very unsure about this one
) -> None:
    # - Init dispatcher

    dp = Dispatcher()

    # - Init crowd

    crowd = Crowd()

    # - Register handlers

    dp.callback_query.register(
        crowd.global_callback_query_handler
    )  # assume no early response can come from callback query
    dp.message.register(
        crowd.get_global_message_handler(
            command_starters=command_starters,
            message_starter=message_starter,
            on_early_response=on_early_response,
        )
    )

    # - Init bot from token if needed

    if isinstance(bot, str):
        bot = Bot(
            token=bot,
            default=default_bot_properties,
        )

    # - Set commands for bot

    # it's possible take from command_starter docs, but `bot_set_my_commands` might takes a while (like ~1s). For not waiting every test, it's just easier to pass it as an argument directly and omit it for tests
    if commands is not None:
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
