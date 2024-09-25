import asyncio

from teletalk.app import App
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


async def increment(response: Response):
    # - Get state

    state = await response.get_chat_state()

    # - Send state message

    await response.tell(f"Counter: {state.get('counter', 0)}")

    # - Increment counter

    state["counter"] = state.get("counter", 0) + 1

    # - Set state

    await response.set_chat_state(state)


async def main():
    deps = TestDeps.load()
    async with App(state_backend="rocksdict", state_config={"path": "/tmp/teletalk__state.py"}) as app:
        # need to use context manager to start the state backend

        await app.start_polling(
            bot=TestDeps.load().config.telegram_bot_token,
            initial_starters={deps.config.telegram_test_chat_id: increment},
            message_starter=increment,
        )


def test():
    asyncio.run(main())


if __name__ == "__main__":
    test()
