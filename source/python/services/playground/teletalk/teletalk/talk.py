import asyncio
import uuid

from asyncio import Future
from typing import TYPE_CHECKING, Any, Callable, Coroutine, List, Literal, Optional

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from loguru import logger
from teletalk.models.bundle_message import BundleMessage
from teletalk.models.callback_info import CallbackInfo
from teletalk.models.multi_query import MultiQuery
from teletalk.models.query import Query
from teletalk.models.response import Response


if TYPE_CHECKING:
    from teletalk.app import App

# todo maybe: 2024-09-12, add default_commands for each talk so that the commands would update to match the focus talk [@marklidenberg]


class Talk:
    def __init__(
        self,
        coroutine: Coroutine,
        app: "App",  # each talk has a full access to the app, mostly for managing the talks
        default_reply_keyboard_markup: Optional[ReplyKeyboardMarkup] = None,
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
        self.default_reply_keyboard_markup = default_reply_keyboard_markup  # default keyboard menu of the talk. Will appear if the query does not have a menu

        # - Call tree

        self.parent: Optional[Talk] = None
        self.children: list[Talk] = []

        # - State

        self.reply_keyboard_markups: dict[str, ReplyKeyboardMarkup] = {}  # may be different for different chats
        self.callback_infos: dict[str, CallbackInfo] = {}
        self.bundle_messages: list[BundleMessage] = []  # List of messages related to ongoing queries

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
        query: Optional[Query | MultiQuery] = None,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
    ) -> Any:
        # - Render the query messages and `reply_keyboard_markup`

        # - Update talk `self.reply_keyboard_markups` from the rendered messages and the `self.default_reply_keyboard_markup`

        # - Run `self.upsert_bundle_messages` with the rendered messages

        # - Wait for the `RawResponse` event from the global callbacks

        # - Build `Response` and run and return appropriate callback

        pass

    async def upsert_bundle_messages(
        self,
        bundle_messages: list[BundleMessage],
        update_mode: Literal["inplace", "inplace_recent", "create_new"],
    ):
        pass

    async def receive_response(
        self,
        response: Response,
    ):
        # - Add response to the input channel

        pass

    async def tell(self, **kwargs) -> None:
        # - The interface to send custom messages without awaiting any response

        pass
