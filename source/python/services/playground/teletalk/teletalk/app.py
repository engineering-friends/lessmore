from typing import Callable, Optional

import aiogram

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, CallbackQuery, Message
from teletalk.models.response import Response
from teletalk.talk import Talk


class App:
    """An entrypoint class for the teletalk application.

    Features:
    - `start_polling` is the main entry point for the application
    - Stores, manages and creates new `Talk` instances
    - Handles message updates and callback queries: update chat focus and sends the `Response` to the dispatcher


    The flow.
    - `App` contains current `Talk`s, which are spread across the chats
    - A `Talk` is basically a coroutine. When the coroutine is finished, the `Talk` is removed from the `App`
    - The interaction with telegram is done in declarative way: we define the `Page` object (containing the `Block`s) and set current page of the `Talk`, which creates, updates and deletes the appropriate messages, defined by the `Block`s of the `Page`. `Block`s render themselves to `BlockMessage`s, which maybe be converted to the telegram messages.
    - Within the `Talk` flow there are two ways to interact with the user:
        - `Talk.ask` method, which updates the active `Page` and waits for the `Response`
        - `Talk.tell` method, which just updates the active `Page`
    - The `Talk` keeps all the messages in the `Talk.history` (that may contain messages out of the current `Talk.active_page`) and the `Talk.active_page` is the page that is currently being displayed to the user
    """

    def __init__(self):
        # - State

        self.talks: list[Talk] = []
        self.focus_talks: dict[str, Talk] = {}

    async def start_new_talk(
        self,
        starter: Callable,
        initial_response: Optional[Response] = None,
    ):
        # - Create the talk

        # - Run the starter and wait for the result

        # - Remove the talk

        pass

    async def on_callback_query(
        self,
        callback_query: CallbackQuery,
    ) -> None:
        # - Build the `Response` and send it to the dispatcher

        pass

    async def on_message(
        self,
        message: Message,
    ) -> None:
        # - If the message is from the bot, update the chat talk focus and return

        # - Otherwise, build the `Response` with a flattened block_message (one message in one block_message, e.g. for 3-message album make separate 3 block_messages) and send it to the dispatcher

        pass

    async def on_delete_message(
        self,
        message: Message,
    ) -> None:
        # - If the message is from the bot, update the chat talk focus and return

        pass

    async def _update_focus(self, chat_id: int) -> None:
        # - Set the chat menu as the menu of the talk with the latest message

        pass

    async def start_polling(
        self,
        bot: Bot | str,
        message_starter: Callable,  # def message_starter(response: Response) -> None
        command_starters: dict[str, Callable] = {},  # def command_starter(response: Response) -> None
        dispatcher: Optional[Callable] = None,
        default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
        commands: Optional[list[BotCommand]] = None,  # description of commands
    ) -> None:
        # - Init aiogram dispatcher

        # - Init teletalk `dispatcher` if not provided

        # - Register `on_callback_query`, `on_message` and `on_delete_message` handlers in aiogram

        # - Init bot from token if needed

        # - Set commands for the bot

        # - Start polling

        pass
