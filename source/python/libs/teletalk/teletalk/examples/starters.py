import asyncio

from aiogram.types import ReplyKeyboardRemove
from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


def test():
    deps = TestDeps.load()
    asyncio.run(
        App(
            bot=deps.config.telegram_bot_token,
            initial_starters={
                deps.config.telegram_test_chat_id: lambda response: response.tell(
                    "Initial starter", mode="inplace_latest"
                )
            },
            message_starter=lambda response: response.tell("Message starter", mode="inplace_latest"),
            command_starters={"/start": lambda response: response.tell("Command starter", mode="inplace_latest")},
            persistant_state_path="/tmp/state.json",
            # reset_state=True,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
