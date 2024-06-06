import asyncio

from typing import Callable

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from palette.deps.init_deps import init_deps
from palette.teledo.elements.lib.button_element import ButtonElement
from palette.teledo.start_polling.start_polling import start_polling


def test_callback(
    chat_id: int,
    func: Callable,
) -> None:
    async def main():
        # - Init bot

        bot = Bot(
            token=init_deps().config.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

        # - Send test message

        message = await bot.send_message(
            chat_id=chat_id,
            text=f"Testing {func.__name__} callback...",
        )

        # - Run callback

        await func(message)

        # - Start polling

        await start_polling(bot=bot)

    asyncio.run(main())


def test():
    async def callback(message: Message):
        await message.answer("Test passed!")

    test_callback(
        chat_id=init_deps().config.telegram_test_chat_id,
        func=ButtonElement(text="Test Button", callback=callback),
    )


if __name__ == "__main__":
    test()
