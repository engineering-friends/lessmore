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
        message_starter: Optional[Callable] = None,
        command_starters: dict[str, Callable] = {},
        dispatcher: Optional[Callable] = None,  # dispatcher is like a low-level `Talk`
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
            app=self,
            message_starter=message_starter,
            command_starters=command_starters,
        )

        self.default_bot_properties = default_bot_properties
        self.commands = commands

        # - State

        self.talks: list[Talk] = []
        self.messages_by_chat_id: dict[int, list[Message]] = {}

    async def start_new_talk(
        self,
        starter: Callable,
        initial_response: Optional[Response] = None,
        parent_talk: Optional[Talk] = None,
    ):
        # - Create the talk

        talk = Talk(
            coroutine=starter(initial_response),
            app=self,
        )

        if parent_talk:
            talk.parent = parent_talk
            parent_talk.children.append(talk)

        self.talks.append(talk)

        # - Set talk for the initial response

        initial_response.talk = talk

        # - Run the starter and wait for the result

        logger.info("Running talk", talk=talk)

        await talk.coroutine

        # - Remove the talk

        logger.info("Removing talk", talk=talk)

        if talk.parent:
            talk.parent.children.remove(talk)

        self.talks.remove(talk)

    async def on_callback_query(
        self,
        callback_query: CallbackQuery,
    ) -> None:
        # - Build the `Response` and send it to the dispatcher

        await self.dispatcher(
            response=Response(
                chat_id=callback_query.message.chat.id,
                callback_id=callback_query.data,
            ),
        )

        # - Answer the callback query, remove highlighted button effect

        await self.bot.answer_callback_query(callback_query.id)

    async def on_bot_message(self, message: Message) -> None:
        logger.debug("Received new bot message", id=message.message_id, chat_id=message.chat.id, text=message.text)

        self.messages_by_chat_id.setdefault(message.chat.id, []).append(message)

    async def on_message(
        self,
        message: Message,
    ) -> None:
        # - Add message to the messages_by_chat_id

        logger.debug("Received new message", id=message.message_id, chat_id=message.chat.id, text=message.text)

        self.messages_by_chat_id.setdefault(message.chat.id, []).append(message)

        # - Otherwise, build the `Response` with a flattened `BlockMessage` and send it to the `self.dispatcher`

        await self.dispatcher(
            response=Response(
                chat_id=message.chat.id,
                block_messages=[
                    BlockMessage(
                        chat_id=message.chat.id,
                        messages=[message],
                        text=message.text,
                    )
                ],
            ),
        )

    async def start_polling(self) -> None:
        # - Init aiogram dispatcher

        aiogram_dispatcher = Dispatcher()

        # - Register `on_callback_query`, `on_message` and `on_delete_message` handlers in aiogram

        aiogram_dispatcher.callback_query.register(self.on_callback_query)
        aiogram_dispatcher.message.register(self.on_message)

        # - Hook send message method in the bot, to process it with a handler

        # todo maybe: enrich default aiogram instead of monkey patching [@marklidenberg]

        old_send_message = self.bot.send_message

        async def _hooked_send_message(*args, **kwargs):
            message = await old_send_message(*args, **kwargs)
            await self.on_bot_message(message)
            return message

        self.bot.send_message = _hooked_send_message

        # - Set commands for the bot

        if self.commands:
            await self.bot.set_my_commands(self.commands)

        # - Start polling

        await aiogram_dispatcher.start_polling(self.bot)