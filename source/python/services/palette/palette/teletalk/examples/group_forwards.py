import asyncio

from datetime import datetime

from aiogram.types import Message
from lessmore.utils.to_anything.to_datetime import to_datetime
from loguru import logger
from palette.deps import Deps
from palette.teletalk.crowd.response import Response
from palette.teletalk.crowd.talk.talk import Talk
from palette.teletalk.start_polling import start_polling


class Grouper:
    def __init__(self, window_seconds: float = 1):
        self.messages: list[Message] = []
        self.window_seconds = window_seconds

    async def __call__(self, response: Response) -> None:
        if response.message:
            # - Append message

            self.messages.append(response.message)

            logger.debug(f"Message appended: {response.message.text}")

            # - Group

            asyncio.create_task(self.group())

    async def group(self):
        # - Wait

        await asyncio.sleep(self.window_seconds)

        # - Check if we have any messages

        if not self.messages:
            return

        # - Check if the last message is within the window

        if (datetime.now() - to_datetime(self.messages[-1].date)).total_seconds() > self.window_seconds:
            # - Create a copy of messages because we want to clear the list before sending the message

            messages_copy = list(self.messages)

            # - Clear messages

            self.messages = []

            # - Sort messages

            messages_copy = sorted(messages_copy, key=lambda message: message.message_id)

            # - Send the message

            await messages_copy[-1].answer(
                text="Grouped messages: \n" + "\n".join([message.text for message in messages_copy])
            )


def test():
    # - Init grouper

    grouper = Grouper()

    # - Start polling

    asyncio.run(
        start_polling(
            message_starter=grouper,
            on_early_response=grouper,
            bot=Deps.load().config.telegram_bot_token,
        )
    )


if __name__ == "__main__":
    test()
