import asyncio

from typing import TYPE_CHECKING, Any, Callable, Coroutine, List, Literal, Optional

from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions, Message, ReplyKeyboardMarkup
from lessmore.utils.asynchronous.gather_nested import gather_nested
from lessmore.utils.functional.skip_duplicates import skip_duplicates
from loguru import logger
from more_itertools import last
from pymaybe import maybe
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
        prompt: str | Block | Page | Response = "",
        files: Optional[list[str]] = None,
        reply_keyboard_markup: Optional[ReplyKeyboardMarkup] = None,
        inline_keyboard_markup: Optional[
            InlineKeyboardMarkup
        ] = None,  # will return the button value if passed this way
        update_mode: Literal["inplace", "create_new"] = "create_new",
        default_chat_id: int = 0,  # usually passed from the response
        parent_response: Optional[Response] = None,
    ) -> Any:
        # - Build the `Page` from the `text`, `files`, `reply_keyboard_markup`, `inline_keyboard_markup` if not provided

        if isinstance(prompt, str):
            page = Page(
                blocks=[
                    SimpleBlock(
                        text=prompt,
                        files=files,
                        reply_keyboard_markup=reply_keyboard_markup,
                        inline_keyboard_markup=inline_keyboard_markup,
                    )
                ]
            )
        elif isinstance(prompt, Block):
            page = Page(blocks=[prompt])
        elif isinstance(prompt, Page):
            page = prompt
        elif isinstance(prompt, Response):
            page = prompt.page
        else:
            raise Exception(f"Unknown prompt type: {type(prompt)}")

        # - Run `self.update_active_page`

        await self.update_active_page(
            page=page,
            update_mode=update_mode,
            default_chat_id=default_chat_id,
        )

        # - Wait for the `Response` in the `self.input_channel`

        response = await self.input_channel.get()

        # - Enrich response with all extra data

        # -- Talk

        response.talk = self

        # -- Blocks

        response.page = self.active_page
        response.root_block = self.active_page.blocks[0] if self.active_page.blocks else None
        response.block = response.root_block

        # -- Navigation

        if not parent_response:
            response.root = response
        else:
            response.root = parent_response.root
            response.previous = parent_response
            parent_response.next = response

        # - Add user messages to the `self.history`

        for block_message in response.block_messages:
            self.history.extend(block_message.messages)

        # - Find the appropriate callback from the `self.page` and their blocks and run it

        if response.callback_id:
            for block in self.active_page.blocks:
                if response.callback_id in block.query_callbacks:
                    return await gather_nested(await block.query_callbacks[response.callback_id](response))
            raise Exception(f"Callback not found: {response.callback_id}")
        else:
            chat_id = response.block_messages[0].chat_id

            # - Find the last block_message in the chat

            last_block = last([block for block in self.active_page.blocks if block.chat_id == chat_id])

            # - Run the last block_message callback

            if last_block.message_callback:
                return await gather_nested(await last_block.message_callback(response))
            else:
                logger.info("No message callback found")

        return response

    async def update_active_page(
        self,
        page: Page,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
        default_chat_id: int = 0,
    ):
        # - Get old block messages

        if self.active_page is not None:
            old_block_messages = [block._render for block in self.active_page.blocks]
        else:
            old_block_messages = []

        for old_block_message in old_block_messages:
            assert len(old_block_message.messages) == 1, "Only single message blocks are supported in all modes for now"

        first_old_message = None if not old_block_messages else old_block_messages[0].messages[0]

        # - Render new block messages. Note: if some blocks are in the self.active_page, their renders will be reset # todo later: bad side effet,

        block_messages = [block.render() for block in page.blocks]

        for block_message in block_messages:
            if not block_message.chat_id:
                block_message.chat_id = default_chat_id
            assert block_message.chat_id, "Block Message has no chat_id"

        # - Upsert message helper function

        async def _upsert_message(block_message: BlockMessage, old_message: Optional[Message] = None):
            # - Edit or send message

            if old_message:
                message = await self.app.bot.edit_message_text(
                    chat_id=block_message.chat_id,
                    message_id=old_message.message_id,
                    text=block_message.text,
                    reply_markup=block_message.inline_keyboard_markup or block_message.reply_keyboard_markup,
                    parse_mode="MarkdownV2",
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )
            else:
                message = await self.app.bot.send_message(
                    chat_id=block_message.chat_id,
                    text=block_message.text,
                    reply_markup=block_message.inline_keyboard_markup or block_message.reply_keyboard_markup,
                    parse_mode="MarkdownV2",
                    link_preview_options=LinkPreviewOptions(is_disabled=True),
                )

            # - Track message

            block_message.messages = [message]

            self.history = list(
                sorted(
                    skip_duplicates(block_message.messages + self.history, key=lambda message: message.message_id),
                    key=lambda message: message.message_id,
                ),
            )

        # - Process update modes

        # -- Create new

        if update_mode == "create_new":
            for block_message in block_messages:
                await _upsert_message(block_message=block_message)

        # -- Inplace recent

        elif update_mode == "inplace_recent":
            # - Get block_message

            assert len(block_messages) == 1, "Only single message blocks are supported in inplace_recent mode"
            block_message = block_messages[0]

            # - Check if the current message is the latest

            if (
                first_old_message
                and int(maybe(self.app.messages_by_chat_id)[block_message.chat_id][-1].message_id.or_else(0))
                == first_old_message.message_id
            ):
                await _upsert_message(block_message=block_message, old_message=first_old_message)

            else:
                await _upsert_message(block_message=block_message)

        # -- Inplace

        elif update_mode == "inplace":
            assert len(block_messages) == 1, "Only single message blocks are supported in inplace mode"
            await _upsert_message(
                block_message=block_messages[0],
                old_message=first_old_message,
            )

        # -- Inplace by id

        elif update_mode == "inplace_by_id":
            _old_block_messages_by_id = {
                block.id: old_block_messages[i] for i, block in enumerate(self.active_page.blocks)
            }
            for block in page.blocks:
                if old_block_message := _old_block_messages_by_id.get(block.id):
                    _first_old_message = old_block_message.messages[0]
                else:
                    _first_old_message = None

                await _upsert_message(block_message=block._render, old_message=_first_old_message)

        # -- Not implemented

        else:
            raise Exception(f"Not implemented update_mode: {update_mode}")

        # - Set active page attribute

        self.active_page = page

        logger.debug("Updated active page", messages=block_messages[0].messages)

    async def receive_response(
        self,
        response: Response,
    ):
        # - Add response to the input channel

        await self.input_channel.put(response)

    async def tell(
        self,
        prompt: str | Block | Page | Response = "",
        files: Optional[list[str]] = None,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
        default_chat_id: int = 0,  # usually passed from the response
    ) -> None:
        # - The interface to send custom messages without awaiting any response

        # todo later: make proper entities for the input [@marklidenberg]

        if isinstance(prompt, str):
            page = Page(
                blocks=[
                    SimpleBlock(
                        text=prompt,
                        files=files,
                    )
                ]
            )
        elif isinstance(prompt, Block):
            page = Page(blocks=[prompt])
        elif isinstance(prompt, Page):
            page = prompt
        elif isinstance(prompt, Response):
            page = prompt.page
        else:
            raise Exception(f"Unknown prompt type: {type(prompt)}")

        await self.update_active_page(
            page=page,
            update_mode=update_mode,
            default_chat_id=default_chat_id,
        )

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
