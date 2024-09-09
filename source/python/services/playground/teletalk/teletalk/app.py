from typing import Callable, Optional

import aiogram

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, CallbackQuery, Message
from teletalk.dispatch import Dispatcher as TeleTalkDispatcher
from teletalk.talk import Talk


class App:
    """An entrypoint class for the TeleTalk application.

    Features:
    - `start_polling` is the main entry point for the application
    - Stores, manages and creates new Talk instances
    - Handles incoming messages
       - updating the chat talk focus (menu is shown for the focused talk in the chat, which corresponds to the latest message)
       - collecting a batch of user messages and sending it to the supervisor talk
    - Handles incoming callback queries, sending them to the relevant Talk instance
    """

    def __init__(self):
        # - State

        self.talks: list[Talk] = []

    async def start_new_talk(
        self,
        starter: Callable,
        starter_messages: list[Message] = [],
    ):
        # - Create the talk

        # - Build the response, run the starter and wait for the result

        # - Remove the talk

        pass

    async def on_callback_query(
        self,
        callback_query: CallbackQuery,
    ) -> None:
        # - Build the response and dispatch it

        pass

    async def on_new_message(
        self,
        message: Message,
    ) -> None:
        # - If the message is from the bot, update the chat talk focus and return

        # - Otherwise, build the response and dispatch it

        pass

    async def update_focus(self, chat_id: int) -> None:
        # - Set the chat menu as the menu of the talk with the latest message

        pass

    async def start_polling(
        self,
        bot: Bot | str,
        message_starter: Callable,
        command_starters: dict[str, Callable] = {},
        dispatcher: Optional[Callable] = None,
        default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
        commands: Optional[list[BotCommand]] = None,  # description of commands
    ) -> None:
        # - Init aiogram dispatcher

        # - Init teletalk `dispatcher` if not provided

        # - Register `callback_query` and `message` handlers in aiogram. Also, register updating the focus on deletion of the message

        # - Init bot from token if needed

        # - Set commands for the bot

        # - Start polling

        pass
