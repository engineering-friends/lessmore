import asyncio

from typing import Optional

from aiogram.types import Message
from palette.deps import Deps
from palette.teletalk.crowd.talk import Talk
from palette.teletalk.query.query import Query
from palette.teletalk.query.zoo.button import Button
from palette.teletalk.start_polling.start_polling import start_polling


async def command_starter(talk: Talk, message: Message) -> None:
    # - Main callback function

    async def increment(
        talk: Talk,
        root_query: Query,
        query: Button,
    ):
        # - Simulate some processing time

        await asyncio.sleep(1)

        # - Write a message for the user

        await talk.message.answer(
            text="I'm incrementing the number by 1, buddy! Also I'll spawn another talk in parallel, just for fun"
        )

        # - Increment button state by 1

        query.label_text = str(int(query.label_text) + 1)

        # - Spawn another talk in parallel (just for fun)

        talk.start_new_talk(callback=command_starter)

        # - Ask the query again with updated state

        return await talk.ask(query=root_query)

    async def quit(
        talk: Talk,
        message: Message,
        root_query: Query,
        query: Button,
    ):
        query.label_text = "You was supposed to press me! Bye!"
        await talk.question_message.edit_text(**root_query.render(talk=talk).__dict__)
        await asyncio.sleep(2)
        await talk.question_message.delete()

    # - Create a button

    await talk.ask(
        query=Button(
            button_text="Increment!",
            label_text="0",
            callback=increment,
            message_callback=quit,
        ),
    )


def test():
    asyncio.run(
        start_polling(
            command_starters={"/start": command_starter},
            bot=Deps.load().config.telegram_bot_token,
        )
    )


if __name__ == "__main__":
    test()
