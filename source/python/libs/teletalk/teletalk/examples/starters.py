import asyncio

from aiogram.types import ReplyKeyboardRemove
from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


def build_starter(text: str, chat_id: int = 0):
    async def starter(response: Response):
        if chat_id:
            response.chat_id = chat_id
        await response.tell(text)

    return starter


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            initial_starters=[build_starter(text="Initial starter", chat_id=160773045)],
            message_starter=build_starter(text="Message starter"),
            command_starters={"/start": build_starter(text="Command starter")},
        ).start_polling()
    )


if __name__ == "__main__":
    test()
