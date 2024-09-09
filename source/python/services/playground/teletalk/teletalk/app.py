from typing import Callable, Optional

import aiogram

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, CallbackQuery, Message
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
        self.message_buffers_by_chat_id: dict[int, list[Message]] = {}

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

    async def on_new_message(
        self,
        message: Message,
    ) -> None:
        # - If the message is from the bot, update the chat talk focus and return

        # - Otherwise, process user message

        # -- Send the message to the buffer of the chat

        # -- Close the buffer if needed and send the event to the supervisor talk (the first talk)

        # -- Create timers if needed to try to close the buffer

        pass

    async def update_chat_talk_focus(self, chat_id: int) -> None:
        # - Set the chat menu as the menu of the talk with the latest message

        pass

    async def start_polling(
        self,
        bot: Bot | str,
        default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
        commands: Optional[list[BotCommand]] = None,  # description of commands
    ) -> None:
        # - Init dispatcher

        # - Register callback_query and message handlers

        # - Start the supervisor talk

        # - Init bot from token if needed

        # - Set commands for the bot

        # - Start polling

        pass
