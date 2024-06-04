import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from repos.lessmore.source.python.services.palette.palette.deps.init_deps import init_deps


dp = Dispatcher()  # All handlers should be attached to the Router (or Dispatcher)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def reverse_echo_handler(message: Message) -> None:
    await message.answer(message.text[::-1])


async def main() -> None:
    # - Init deps

    deps = init_deps()

    # - Initialize Bot instance with default bot properties which will be passed to all API calls

    bot = Bot(
        token=deps.config.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # - And the run events dispatching

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
