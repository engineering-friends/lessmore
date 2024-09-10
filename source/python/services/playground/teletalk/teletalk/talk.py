import asyncio
import uuid

from asyncio import Future
from typing import TYPE_CHECKING, Any, Callable, Coroutine, List, Literal, Optional

from loguru import logger
from teletalk.callback_info import CallbackInfo
from teletalk.query import Query
from teletalk.question_message import QuestionMessage
from teletalk.response import Response


if TYPE_CHECKING:
    from teletalk.app import App


class Talk:
    def __init__(
        self,
        coroutine: Coroutine,
        app: "App",  # each talk has a full access to the app, mostly for managing the talks
        default_menu: Optional[Any] = None,
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
        self.default_menu = (
            default_menu  # default keyboard menu of the talk. Will appear if the query does not have a menu
        )

        # - Call tree

        self.parent: Optional[Talk] = None
        self.children: list[Talk] = []

        # - State

        self.question_messages: list[QuestionMessage] = []  # List of messages related to ongoing queries
        self.question_callbacks: list[
            CallbackInfo
        ] = []  # List of callbacks related to ongoing queries for all messages

        self.menus = []  # List of menus related to ongoing queries (for different chats)
        self.history = []  # History of interactions within the talk
        self.input_channel = asyncio.Queue()  # queue to manage asynchronous events

    def ask(
        self,
        query: Query,
        update_mode: Literal["inplace", "inplace_recent", "create_new"] = "create_new",
    ) -> Any:
        # - Render the query messages and menus, update `self.question_messages` and `self.menus`

        # - Update messages in telegram according to the `update_mode`. Add new messages to `self.question_messages and self.history`

        # - Wait for the `raw_response` event from the global callbacks

        # - Apply `on_query_reply` for each message (spawn tasks in parallel)

        # - Build `response` and run and return appropriate callback

        pass

    async def receive_response(
        self,
        response: Response,
    ):
        # - Add response to the input channel

        pass

    def tell(self, **kwargs) -> None:
        # - Send the messages and add them to the `self.history`

        pass
