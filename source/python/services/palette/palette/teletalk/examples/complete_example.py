import asyncio

from aiogram.types import Message
from palette.deps import Deps
from palette.teletalk.crowd.response import Response
from palette.teletalk.crowd.talk.talk import Talk
from palette.teletalk.query.query import Query
from palette.teletalk.query.zoo.button import Button
from palette.teletalk.start_polling import start_polling


async def command_starter(response: Response) -> None:
    # - Main callback function

    async def increment(response: Response):
        # - Simulate some processing time

        await asyncio.sleep(1)

        # - Write a message for the user

        await response.tell.answer(
            text="I'm incrementing the number by 1, buddy! Also I'll spawn another talk in parallel, just for fun"
        )

        # - Increment button state by 1

        response.query.label_text = str(int(response.query.label_text) + 1)

        # - Spawn another talk in parallel (just for fun)

        response.start_new_talk(callback=command_starter)

        # - Ask the query again with updated state

        return await response.ask(query=response.root_query)

    async def quit(response: Response):
        response.query.label_text = "You was supposed to press me! Bye!"
        await response.question_message.edit_text(**response.root_query.render(talk=response.talk).to_dict())
        await asyncio.sleep(2)
        await response.question_message.delete()

    # - Create a button

    await response.ask(
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
