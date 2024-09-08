from typing import Callable, Optional

import aiogram

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, CallbackQuery, Message


class App:
    def __init__(self):
        self.talks = []

    async def start_new_talk(self, starter: Callable, starter_kwargs: dict):
        # - Create talk and add it to the list

        pass

        # - Run the starter

        pass

        # - Remove the talk from the list

        pass

    async def on_callback_query(self, callback_query: CallbackQuery) -> None:
        # - Find the talk by message_id

        pass

        # - Send the event to the talk

        pass

    async def on_message(self, message: Message) -> None:
        # - Send the message to the buffer of the chat

        pass

        # - Close the buffer if needed

        pass

        # -- Find the talk by message_id

        pass

        # -- Send the event to the talk

        pass

        # - Create timers if needed to try to close the buffer

        pass

    async def start_polling(
        self,
        bot: Bot | str,
        default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
        commands: Optional[list[BotCommand]] = None,  # description of commands
    ) -> None:
        # - Init dispatcher

        dp = Dispatcher()

        # - Register handlers

        dp.callback_query.register(self.on_callback_query)
        dp.message.register(self.on_message)

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
