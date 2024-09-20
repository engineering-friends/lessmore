import asyncio

from aiogram.types import ReplyKeyboardRemove
from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


def build_starter(text: str, chat_id: int = 0):
    async def starter(response: Response):
        if chat_id:
            await response.tell(text, default_chat_id=chat_id)
        else:
            await response.tell(text)

    return starter


def test():
    deps = TestDeps.load()
    asyncio.run(
        App(
            bot=deps.config.telegram_bot_token,
            initial_starters=[build_starter(text="Initial starter", chat_id=deps.config.telegram_test_chat_id)],
            message_starter=build_starter(text="Message starter"),
            command_starters={"/start": build_starter(text="Command starter")},
            persistant_state_path="/tmp/state.json",
            # reset_state=True,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
