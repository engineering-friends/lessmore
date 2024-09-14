import asyncio

from typing import TYPE_CHECKING, Any, Callable, Coroutine, List, Literal, Optional

from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from teletalk.models.block import Block
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
        - Talk may receive response from outside (usually, from the supervisor)

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

        self.input_channel = asyncio.Queue()  # a queue of input `RawResponse` objects

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
        # - Build page from the `text`, `files`, `reply_keyboard_markup`, `inline_keyboard_markup` if not provided

        # - Run `self.update_active_page`

        # - Wait for the `Response` in the `self.input_channel`

        # - Add user messages to the `self.history`

        # - Find the appropriate callback from the `self.page` and their blocks and run it

        pass

    def update_active_page(
        self,
        page: Page,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
    ):
        # - Render all the blocks

        # - Update the messages in line with `update_mode`. Add new messages to `self.history`

        pass

    async def receive_response(
        self,
        response: Response,
    ):
        # - Add response to the input channel

        pass

    async def tell(
        self,
        text: Optional[str] = None,
        files: Optional[list[str]] = None,
        page: Optional[Page | Block | Response] = None,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
    ) -> None:
        # - The interface to send custom messages without awaiting any response

        pass
