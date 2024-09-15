from typing import Callable, Optional

import aiogram

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, CallbackQuery, Message
from loguru import logger
from teletalk.dispatcher import Dispatcher as TeletalkDispatcher
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response
from teletalk.talk import Talk


class App:
    """An entrypoint class for the teletalk application.

    Features:
    - `start_polling` is the main entry point for the application
    - Stores, manages and creates new `Talk` instances
    - Handles message updates and callback queries: sends the `Response` to the dispatcher


    The flow.
    - `App` contains current `Talk`s, which are spread across the chats
    - A `Talk` is basically a coroutine. When the coroutine is finished, the `Talk` is removed from the `App`
    - The interaction with telegram is done in declarative way: we define the `Page` object (containing the `Block`s) and set current page of the `Talk`, which creates, updates and deletes the appropriate messages, defined by the `Block`s of the `Page`. `Block`s render themselves to `BlockMessage`s, which maybe be converted to the telegram messages.
    - Within the `Talk` flow there are two ways to interact with the user:
        - `Talk.ask` method, which updates the active `Page` and waits for the `Response`, enriches it, and then runs the appropriate callback
        - `Talk.tell` method, which just updates the active `Page`
    - The `Talk` keeps all the messages in the `Talk.history` (that may contain messages out of the current `Talk.active_page`) and the `Talk.active_page` is the page that is currently being displayed to the user
    """

    def __init__(
        self,
        bot: Bot | str,
        message_starter: Callable,
        command_starters: dict[str, Callable] = {},
        dispatcher: Optional[Callable] = None,
        default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.HTML),
        commands: Optional[list[BotCommand]] = None,
    ):
        # - Args

        if isinstance(bot, Bot):
            self.bot = bot
        elif isinstance(bot, str):
            self.bot = Bot(bot, default=default_bot_properties)
        else:
            raise Exception("Unknown bot type")

        self.message_starter = message_starter
        self.command_starters = command_starters
        self.dispatcher = dispatcher or TeletalkDispatcher(
            message_starter=message_starter,
            command_starters=command_starters,
        )

        self.default_bot_properties = default_bot_properties
        self.commands = commands

        # - State

        self.talks: list[Talk] = []

    async def start_new_talk(
        self,
        starter: Callable,
        initial_response: Optional[Response] = None,
    ):
        # - Create the talk

        talk = Talk(
            coroutine=starter(initial_response),
            app=self,
        )
        self.talks.append(talk)

        # - Run the starter and wait for the result

        logger.info("Running talk", talk=talk)

        await talk.coroutine

        # - Remove the talk

        logger.info("Removing talk", talk=talk)

        self.talks.remove(talk)

    async def on_callback_query(
        self,
        callback_query: CallbackQuery,
    ) -> None:
        # - Build the `Response` and send it to the dispatcher

        await self.dispatcher(
            talks=self.talks,
            response=Response(callback_id=callback_query.data),
        )

    async def on_message(
        self,
        message: Message,
    ) -> None:
        # - Otherwise, build the `Response` with a flattened `BlockMessage` and send it to the `self.dispatcher`

        await self.dispatcher(
            talks=self.talks,
            response=Response(
                block_messages=[
                    BlockMessage(
                        chat_id=str(message.chat.id),
                        messages=[message],
                        text=message.text,
                        files=message.media,
                    )
                ]
            ),
        )

    async def start_polling(self) -> None:
        # - Init aiogram dispatcher

        aiogram_dispatcher = Dispatcher()

        # - Register `on_callback_query`, `on_message` and `on_delete_message` handlers in aiogram

        aiogram_dispatcher.callback_query.register(self.on_callback_query)
        aiogram_dispatcher.message.register(self.on_message)

        # - Set commands for the bot

        if self.commands:
            await self.bot.set_my_commands(self.commands)

        # - Start polling

        await aiogram_dispatcher.start_polling(self.bot)
