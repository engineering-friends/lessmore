import asyncio

from aiogram.types import Message
from palette.deps.init_deps import init_deps
from palette.teledo.start_polling import start_polling


async def start(message: Message) -> None:
    await message.answer(f"Hello, Mark Lidenberg!")


async def echo(message: Message) -> None:
    await message.answer(message.text[::-1])


async def main() -> None:
    await start_polling(
        bot=init_deps().config.telegram_bot_token,
        command_handlers={
            "start": start,
            "echo": echo,
        },
    )


if __name__ == "__main__":
    asyncio.run(main())
