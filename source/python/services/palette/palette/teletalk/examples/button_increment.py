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
        await asyncio.sleep(5)
        root_query.text = str(int(root_query.text) + 1)
        return await talk.ask(query=root_query)  # run the query again

    # - Create a button

    await talk.ask(query=Button(text="0", callback=increment))


def test():
    asyncio.run(
        start_polling(
            command_starters={"/start": command_starter},
            bot=Deps.load().config.telegram_bot_token,
        )
    )


if __name__ == "__main__":
    test()
