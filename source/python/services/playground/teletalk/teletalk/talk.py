import asyncio

from typing import TYPE_CHECKING, Any, Callable, Coroutine, List, Literal, Optional

from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from loguru import logger
from more_itertools import last
from teletalk.blocks.simple_block import SimpleBlock
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage
from teletalk.models.page import Page
from teletalk.models.response import Response


if TYPE_CHECKING:
    from teletalk.app import App

# todo maybe: 2024-09-12, add default_commands for each talk so that the commands would update to match the focus talk [@marklidenberg]


class Talk:
    def __init__(
        self,
        coroutine: Coroutine,
        app: "App",  # each talk has a full access to the app, mostly for managing the talks
    ):
        """Talk is a core entity for interaction between the bot an a user, usually in a ask-reply manner.

        Features:
        - Talk keeps track of all the message history
        - Talk handles questions for the user
        - Talk may receive response from the dispatcher

        """

        # - Args

        self.coroutine = coroutine
        self.app = app

        # - Call tree

        self.parent: Optional[Talk] = None
        self.children: list[Talk] = []

        # - State

        self.active_page: Optional[Page] = None
        self.history: list[Message] = []

        # - Input channel for communication

        self.input_channel = asyncio.Queue()  # a queue of input `Response` objects

    async def ask(
        self,
        text: Optional[str] = None,
        files: Optional[list[str]] = None,
        reply_keyboard_markup: Optional[ReplyKeyboardMarkup] = None,
        inline_keyboard_markup: Optional[
            InlineKeyboardMarkup
        ] = None,  # will return the button value if passed this way
        page: Optional[Page | Block | Response] = None,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
    ) -> Any:
        # - Build the `Page` from the `text`, `files`, `reply_keyboard_markup`, `inline_keyboard_markup` if not provided

        if not isinstance(page, Page):
            page = Page(
                blocks=[
                    SimpleBlock(
                        text=text,
                        files=files,
                        reply_keyboard_markup=reply_keyboard_markup,
                        inline_keyboard_markup=inline_keyboard_markup,
                    )
                ]
            )

        # - Run `self.update_active_page`

        await self.update_active_page(page=page, update_mode=update_mode)

        # - Wait for the `Response` in the `self.input_channel`

        response = await self.input_channel.get()

        # - Enrich response with all extra data

        response.talk = self
        response.root_page = self.active_page
        response.root_block = self.active_page.blocks[0] if self.active_page.blocks else None
        response.block = response.root_block

        # - Add user messages to the `self.history`

        for block_message in response.block_messages:
            self.history.extend(block_message.messages)

        # - Find the appropriate callback from the `self.page` and their blocks and run it

        if response.callback_id:
            for block in self.active_page.blocks:
                if response.callback_id in block.query_callbacks:
                    return await block.query_callbacks[response.callback_id](response)
            raise Exception(f"Callback not found: {response.callback_id}")
        else:
            chat_id = response.block_messages[0].chat_id

            # - Find the last block_message in the chat

            last_block = last([block for block in self.active_page.blocks if block.chat_id == chat_id])

            # - Run the last block_message callback

            if last_block.message_callback:
                return await last_block.message_callback(response)
            else:
                logger.info("No message callback found")

        return response

    async def update_active_page(
        self,
        page: Page,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
    ):
        # - Render all the blocks

        rendered_blocks = [block.render() for block in page.blocks]

        # - Update the messages in line with `update_mode`. Add new messages to `self.history`

        if update_mode == "create_new":
            self.active_page = page
            for block_message in rendered_blocks:
                # - Send messages to telegram using aiogram

                message = await self.app.bot.send_message(
                    entity=block_message.chat_id,
                    message="\n".join([message.text for message in block_message.messages]),
                    parse_mode="md",
                    link_preview=False,
                )

                block_message.messages.append(message)
                self.history.extend([message])
        else:
            raise Exception(f"Not implemented update_mode: {update_mode}")

    async def receive_response(
        self,
        response: Response,
    ):
        # - Add response to the input channel

        await self.input_channel.put(response)

    async def tell(
        self,
        text: Optional[str] = None,
        files: Optional[list[str]] = None,
        page: Optional[Page | Block | Response] = None,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
    ) -> None:
        # - The interface to send custom messages without awaiting any response

        if not isinstance(page, Page):
            page = Page(
                blocks=[
                    SimpleBlock(
                        text=text,
                        files=files,
                    )
                ]
            )

        await self.update_active_page(page=page, update_mode=update_mode)

    async def start_new_talk(
        self,
        starter: Callable,
        initial_response: Optional[Response] = None,
    ):
        return await self.app.start_new_talk(
            starter=starter,
            initial_response=initial_response,
            parent_talk=self,
        )
