import asyncio

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from palette.aiogram_playground.elements.element import ButtonElement, callbacks
from palette.deps.init_deps import init_deps


async def command_start_handler(message: Message) -> None:
    message_kwargs = ButtonElement("I'm a button!").render().__dict__
    message_kwargs["text"] = message_kwargs.get("text") or "-"
    await message.answer(**message_kwargs)


async def global_handler(callback_query: CallbackQuery) -> None:
    message_kwargs = callbacks[callback_query.callback_data]().render().__dict__
    message_kwargs["text"] = message_kwargs.get("text") or "-"
    await callback_query.message.edit_text(**message_kwargs)
    await callback_query.answer()


async def main() -> None:
    # - Init deps

    deps = init_deps()

    # - Initialize Bot instance with default bot properties which will be passed to all API calls

    dp = Dispatcher()  # All handlers should be attached to the Router (or Dispatcher)

    # - Register handlers

    dp.message.register(command_start_handler, CommandStart())
    dp.message.register(global_handler)

    # - Start polling

    await dp.start_polling(
        Bot(
            token=deps.config.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
