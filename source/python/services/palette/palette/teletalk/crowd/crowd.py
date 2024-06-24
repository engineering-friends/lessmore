from dataclasses import dataclass, field
from typing import Callable, Optional

from aiogram.types import CallbackQuery, Message
from loguru import logger
from more_itertools import last

from palette.teletalk.crowd.chat import Chat
from palette.teletalk.crowd.response import Response


@dataclass
class Crowd:
    chats: dict[int, Chat] = field(default_factory=dict)

    def get_chat(self, user_id: int) -> Chat:
        return self.chats.setdefault(user_id, Chat())

    async def global_callback_query_handler(self, callback_query: CallbackQuery) -> None:
        logger.debug(
            "Callback query received",
            user_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            data=callback_query.data,
        )

        # - Get user context

        chat = self.get_chat(user_id=callback_query.from_user.id)

        # - Get talk with the same message id

        talk = chat.get_talk(question_message=callback_query.message)

        if not talk:
            logger.error(
                "Failed to find talk for callback query",
                user_id=callback_query.from_user.id,
                message_id=callback_query.message.message_id,
                callback_id=callback_query.data,
            )
            return

        # - Send callback event to the coroutine

        await talk.respond(response=Response(callback_id=callback_query.data))

    def get_global_message_handler(
        self,
        command_starters: dict[str, Callable] = {},  # {'/start': def f(response: Response): ...}
        message_starter: Optional[Callable] = None,  # def f(response: Response): ...) -> callable:
        on_early_response: Optional[Callable] = None,  # def f(response: Response): ...
    ) -> Callable:
        async def global_message_handler(message: Message) -> None:
            logger.debug(
                "Message received",
                user_id=message.from_user.id,
                message_id=message.message_id,
                text=message.text,
            )

            # - Get user context

            chat = self.get_chat(user_id=message.from_user.id)

            # - If starter command: start new talk with command

            if message.text.startswith("/"):
                command = message.text.split()[0]
                if command in command_starters:
                    chat.start_new_talk(starter_message=message, callback=command_starters[command])
                    return

            #  - If reply and replied message is a pending question: send to reply talk

            if message.reply_to_message:
                talk = chat.get_talk(question_message=message.reply_to_message)

                if talk:
                    await talk.respond(
                        response=Response(message=message),
                        on_early_response=on_early_response,
                    )
                    return

            # - If there is an talk for latest question message id: send to corresponding talk

            talk = last(chat.talks, default=None)

            if talk:
                await talk.respond(
                    response=Response(message=message),
                    on_early_response=on_early_response,
                )
                return

            # - Start new message by default if there is a message starter

            if not message_starter:
                logger.debug(
                    "No message starter",
                    user_id=message.from_user.id,
                    message_id=message.message_id,
                    text=message.text,
                )
                return

            chat.start_new_talk(starter_message=message, callback=message_starter)

        return global_message_handler
