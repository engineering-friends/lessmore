import asyncio

from asyncio import iscoroutinefunction
from typing import TYPE_CHECKING, Any, Callable, Coroutine, List, Literal, Optional

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, LinkPreviewOptions, Message, ReplyKeyboardMarkup
from lessmore.utils.asynchronous.gather_nested import gather_nested
from lessmore.utils.functional.skip_duplicates import skip_duplicates
from loguru import logger
from more_itertools import last
from pymaybe import maybe
from teletalk.blocks.simple_block import SimpleBlock, build_default_message_callback, default_on_response
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
        keyboard: Optional[ReplyKeyboardMarkup | list[list[str]]] = None,
        one_time_keyboard: bool = True,
        inline_keyboard: Optional[InlineKeyboardMarkup | list[list[str | tuple[str, Callable]]]] = None,
        message_callback: Optional[Callable | str] = "default",
        mode: Literal["inplace", "create_new"] = "create_new",
        default_chat_id: int = 0,  # usually passed from the response
        parent_response: Optional[Response] = None,
        on_response: Optional[Callable] = default_on_response,
    ) -> Any:
        # - Build the `Page` from the prompt data

        if isinstance(prompt, str):
            page = Page(
                blocks=[
                    SimpleBlock(
                        text=prompt,
                        files=files,
                        keyboard=keyboard,
                        one_time_keyboard=one_time_keyboard,
                        inline_keyboard=inline_keyboard,
                        message_callback=message_callback,
                        on_response=on_response,
                    )
                ]
            )
        elif isinstance(prompt, Block):
            page = Page(blocks=[prompt])
        elif isinstance(prompt, Page):
            page = prompt
        elif isinstance(prompt, Response):
            page = prompt.prompt_page
        else:
            raise Exception(f"Unknown prompt type: {type(prompt)}")

        # - Run `self.update_active_page`

        await self.update_active_page(
            page=page,
            mode=mode,
            default_chat_id=default_chat_id,
        )

        # - Wait for the `Response` in the `self.input_channel`

        response = await self.input_channel.get()

        # - Enrich response with all extra data

        # -- Talk

        response.talk = self

        # -- Navigation stack

        if not parent_response.prompt_page:  # starter response
            # First response in the stack

            response.root = response
        else:
            # A continuation response in the stack

            response.root = parent_response.root

            response_stack = parent_response.root.response_stack()

            if _repeated_response := next(
                (
                    _response
                    for _response in response_stack
                    if _response.prompt_page and _response.prompt_page.id == page.id
                ),
                None,
            ):
                # loop call, keep things as is
                response.previous = _repeated_response.previous
                response.next = _repeated_response.next
            else:
                # new element in the stack!

                # - Reset all responses upstream

                a, b = parent_response, parent_response.next
                while b:
                    a.next = None
                    b.previous = None
                    a, b = b, b.next

                # - Set `parent_response.next` to response

                response.previous = parent_response
                parent_response.next = response

        # - Add starter message to the `self.history`

        if parent_response and not parent_response.prompt_page:
            for block_message in parent_response.block_messages:
                self.history.extend(block_message.messages)

        # - Add user messages to the `self.history`

        for block_message in response.block_messages:
            self.history.extend(block_message.messages)

        # - Find the appropriate callback from the `self.page` and their blocks and run it

        if response.callback_id:
            # - Enrich response with the corresponding prompt

            response.prompt_page = page

            for block in self.active_page.blocks:
                for node, parent in block.iter_nodes():
                    if response.callback_id in node.query_callback_infos:
                        response.prompt_sub_block = node
                        response.prompt_block = parent
                        break

                if response.prompt_sub_block:
                    # break early if possible, to avoid unnecessary iteration
                    break

            if not response.prompt_sub_block:
                logger.error("No callback for query")
                return response

            # - Set the callback info

            response.callback_info = response.prompt_sub_block.query_callback_infos[response.callback_id]

            # - Run on_response

            if response.prompt_block.on_response:
                await response.prompt_block.on_response(response)

            # - Run the callback

            return await gather_nested(
                await response.prompt_sub_block.query_callback_infos[response.callback_id].callback(response)
            )

        elif response.block_messages:
            # - Enrich response with the corresponding prompt

            response.prompt_page = page
            response.prompt_block = last(
                [block for block in self.active_page.blocks if block.chat_id == response.block_messages[0].chat_id],
                default=None,
            )  # last block in the chat
            response.prompt_sub_block = response.prompt_block

            # - Validate message callback is present

            if not response.prompt_block:
                logger.error("No block found for chat id")
                return response
            if not response.prompt_block.message_callback:
                logger.warning("No message callback found")
                return await response.ask(mode="inplace")

            # - Run on_response

            if response.prompt_block.on_response:
                await response.prompt_block.on_response(response)

            # - Run the message callback

            return await gather_nested(await response.prompt_sub_block.message_callback(response))

        elif response.external_payload:
            # - Enrich response with the corresponding prompt

            response.prompt_page = page
            response.prompt_block = last(
                [block for block in self.active_page.blocks],
                default=None,
            )  # last block
            response.prompt_sub_block = response.prompt_block

            # - Validate external callback is present

            if not response.prompt_block.external_callback:
                logger.warning("No external callback found")
                return await response.ask(mode="inplace")

            # - Run on_response

            if response.prompt_block.on_response:
                await response.prompt_block.on_response(response)

            # - Run the external callback

            return await gather_nested(await response.prompt_sub_block.external_callback(response))
        else:
            raise Exception("Unknown response type")

    async def upsert_message(
        self,
        block_message: Optional[BlockMessage] = None,
        old_message: Optional[Message] = None,
    ):
        # - Edit or send message

        if old_message:
            if block_message:
                try:
                    logger.debug(
                        "Editing message",
                        chat_id=block_message.chat_id,
                        message_id=old_message.message_id,
                        text=block_message.text,
                        reply_markup=block_message.inline_keyboard_markup
                        if block_message.is_inline_keyboard_visible
                        else None,
                        parse_mode="Markdown",
                        link_preview_options=LinkPreviewOptions(is_disabled=False),
                    )
                    message = await self.app.bot.edit_message_text(
                        chat_id=block_message.chat_id,
                        message_id=old_message.message_id,
                        text=block_message.text,
                        reply_markup=block_message.inline_keyboard_markup
                        if block_message.is_inline_keyboard_visible
                        else None,
                        parse_mode="Markdown",
                        link_preview_options=LinkPreviewOptions(is_disabled=False),
                    )
                except TelegramBadRequest as e:
                    if "Bad Request: message is not modified" in str(e):
                        logger.debug(
                            "Message is not modified, skipping",
                            chat_id=block_message.chat_id,
                            message_id=old_message.message_id,
                        )
                        message = old_message  # just set the message to the old one, as they are the same
                    else:
                        raise
                except Exception as e:
                    logger.exception("Failed to edit message", error=e)
                    raise
            else:
                # no block message, just delete the old message

                message = await self.app.bot.delete_message(
                    chat_id=old_message.chat.id,
                    message_id=old_message.message_id,
                )
                self.history = [message for message in self.history if message.message_id != old_message.message_id]
                return
        else:
            # no old message, create a new one

            message = await self.app.bot.send_message(
                chat_id=block_message.chat_id,
                text=block_message.text,
                reply_markup=block_message.inline_keyboard_markup or block_message.reply_keyboard_markup,
                parse_mode="Markdown",
                link_preview_options=LinkPreviewOptions(is_disabled=False),
            )

        # - Track message

        if isinstance(message, Message):
            block_message.messages = list(
                skip_duplicates(
                    [message] + block_message.messages,
                    key=lambda message: message.message_id,
                ),
            )

            self.history = list(
                sorted(
                    skip_duplicates(block_message.messages + self.history, key=lambda message: message.message_id),
                    key=lambda message: message.message_id,
                ),
            )

    async def update_active_page(
        self,
        page: Page,
        mode: Literal["inplace", "inplace_latest", "create_new"] = "create_new",
        default_chat_id: int = 0,
    ):
        # - Mark blocks for easier usage

        old_page = self.active_page

        old_blocks = old_page.blocks if old_page else []
        new_blocks = page.blocks
        old_only_blocks = [block for block in old_blocks if block.id not in [block.id for block in new_blocks]]
        new_only_blocks = [block for block in new_blocks if block.id not in [block.id for block in old_blocks]]
        common_blocks = [block for block in old_blocks if block.id in [block.id for block in new_blocks]]

        old_blocks_by_old_id = {
            block.id if not block.has_refreshed_id else block.previous_id: block for block in old_blocks
        }

        # - Render new block messages, will fill `current_output` for blocks with refreshed ids

        block_messages = [block.render() for block in new_blocks]  # will affect common_blocks, reset `is_refreshed`

        for block_message in block_messages:
            if not block_message.chat_id:
                block_message.chat_id = default_chat_id
            assert block_message.chat_id, "Block Message has no chat_id"

        # - Get old messages

        old_block_messages = [
            block.current_output
            if block.current_output and block.current_output.messages
            else block.previous_output  # in case we rerendered the blocks
            for block in old_blocks
        ]

        first_old_message = None if not old_block_messages else old_block_messages[0].messages[0]

        # - Process update modes

        # -- Create new

        if mode == "create_new":
            for block_message in block_messages:
                await self.upsert_message(block_message=block_message)

        # -- Inplace recent

        # deprecated logic [@marklidenberg]
        # elif mode == "inplace_recent_one":
        #     # - Get block_message
        #
        #     assert len(block_messages) == 1, "Only single message blocks are supported in inplace_recent_one mode"
        #     block_message = block_messages[0]
        #
        #     # - Check if the current message is the latest
        #
        #     if (
        #         first_old_message
        #         and int(maybe(self.app.messages_by_chat_id)[block_message.chat_id][-1].message_id.or_else(0))
        #         == first_old_message.message_id
        #     ):
        #         await self.upsert_message(block_message=block_message, old_message=first_old_message)
        #
        #     else:
        #         await self.upsert_message(block_message=block_message)

        # -- Inplace recent

        elif mode == "inplace_latest":
            # - Get block_message

            assert len(block_messages) == 1, "Only single message blocks are supported in inplace_latest mode"
            block_message = block_messages[0]

            # - Check if the current message is the latest

            latest_message = maybe(self.app.messages_by_chat_id)[block_message.chat_id][-1].or_else(None)

            if not latest_message or not latest_message.from_user.is_bot:
                # just send a new one
                logger.debug("Sending new message in inplace_latest mode")
                await self.upsert_message(block_message=block_message)
            else:
                logger.debug("Updating message in inplace_latest mode")
                await self.upsert_message(block_message=block_message, old_message=latest_message)

        # -- Inplace by id

        elif mode == "inplace":
            # - Delete old messages

            for block in old_only_blocks:
                for message in [message for message in block.current_output.messages if message.message_id]:
                    await self.upsert_message(block_message=None, old_message=message)

            # - Upsert new messages

            for block in new_blocks:
                if block.id not in old_blocks_by_old_id:
                    _first_old_message = None
                else:
                    _first_old_message = block.previous_output.messages[0]

                await self.upsert_message(block_message=block.current_output, old_message=_first_old_message)

        # -- Not implemented

        else:
            raise Exception(f"Not implemented mode: {mode}")

        # - Set active page attribute

        self.active_page = page

        logger.debug("Updated active page")

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
        keyboard: Optional[ReplyKeyboardMarkup | list[list[str]]] = None,
        mode: Literal["inplace", "inplace_latest", "create_new"] = "create_new",
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
                        keyboard=keyboard,
                    )
                ]
            )
        elif isinstance(prompt, Block):
            page = Page(blocks=[prompt])
        elif isinstance(prompt, Page):
            page = prompt
        elif isinstance(prompt, Response):
            page = prompt.prompt_page
        else:
            raise Exception(f"Unknown prompt type: {type(prompt)}")

        await self.update_active_page(
            page=page,
            mode=mode,
            default_chat_id=default_chat_id,
        )

    async def start_new_talk(
        self,
        starter: Callable,
        initial_response: Optional[Response] = None,
        parallel: bool = False,
    ):
        if not parallel:
            print("Starting new talk in sync")
            return await self.app.start_new_talk(
                starter=starter,
                initial_response=initial_response,
                parent_talk=self,
            )
        else:
            return asyncio.create_task(
                self.app.start_new_talk(
                    starter=starter,
                    initial_response=initial_response,
                    parent_talk=self,
                )
            )

    async def purge(self):
        for message in self.history:
            await self.app.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        self.history = []
