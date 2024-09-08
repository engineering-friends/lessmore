from typing import Callable, Optional

import aiogram

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, CallbackQuery, Message


class App:
    def __init__(self):
        self.talks = []

    async def start_new_talk(
        self,
        starter: Callable,
        starter_message: Optional[Message] = None,
    ):
        # - Create the talk and add it to the list of talks

        # - Run the starter and wait for the result

        # - Remove the talk from the list of talks

        pass

    async def on_callback_query(
        self,
        callback_query: CallbackQuery,
    ) -> None:
        # - Find the talk by message_id

        # - Send the event to the talk

        pass

    async def on_message(
        self,
        message: Message,
    ) -> None:
        # - Send the message to the buffer of the chat

        # - Close the buffer if needed

        # -- Find the talk by message_id

        # -- Send the event to the talk

        # - Create timers if needed to try to close the buffer

        pass

    async def start_polling(
        self,
        bot: Bot | str,
        default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
        commands: Optional[list[BotCommand]] = None,  # description of commands
    ) -> None:
        # - Start supervisor talk

        # - Init dispatcher

        # - Register callback_query and message handlers that redirect events to the supervisor talk

        # - Init bot from token if needed

        # - Set commands for bot

        # - Start polling

        pass
