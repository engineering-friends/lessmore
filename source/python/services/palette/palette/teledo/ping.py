import asyncio

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from palette.deps.init_deps import init_deps


async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


async def reverse_echo_handler(message: Message) -> None:
    await message.answer(message.text[::-1])


async def main() -> None:
    # - Init deps

    deps = init_deps()

    # - Initialize Bot instance with default bot properties which will be passed to all API calls

    dp = Dispatcher()

    # - Register handlers

    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(reverse_echo_handler)

    # - Start polling

    await dp.start_polling(
        Bot(
            token=deps.config.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
