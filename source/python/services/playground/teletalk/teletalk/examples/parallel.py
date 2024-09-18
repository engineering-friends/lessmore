import asyncio

from teletalk.app import App
from teletalk.blocks.menu import Menu
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def starter(response: Response):
    return await response.ask(
        Menu(
            "Click to spawn another talk",
            grid=[
                [
                    (
                        "New talk!",
                        lambda response: response.start_new_talk(
                            starter=starter, initial_response=response, parallel=True
                        ),
                    ),
                    ("Kill me!", lambda response: response.purge_talk()),
                ]
            ],
        )
    )


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
