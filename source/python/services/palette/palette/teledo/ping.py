import asyncio

from aiogram.types import Message
from palette.deps.init_deps import init_deps
from palette.teledo.elements import ButtonElement, run_element
from palette.teledo.start_polling import start_polling


async def start(message: Message) -> None:
    await message.answer(f"Hello, Mark Lidenberg!")

    async def callback(callback_query):
        await message.answer("Button clicked!")
        return "Success!"

    print(
        "Result",
        await run_element(
            ButtonElement(
                text="Click me",
                callback=callback,
            ),
            message=message,
        ),
    )


async def main() -> None:
    await start_polling(
        bot=init_deps().config.telegram_bot_token,
        command_handlers={
            "start": start,
        },
        message_handler=None,
    )


if __name__ == "__main__":
    asyncio.run(main())
