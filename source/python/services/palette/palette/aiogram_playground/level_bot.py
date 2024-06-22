import asyncio

from aiogram import Bot, Dispatcher, F, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from palette.deps import Deps


async def command_start_handler(message: Message) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Go to Level 2", callback_data="go_to_level_2")
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!", reply_markup=keyboard.as_markup())


async def level_2_handler(callback_query: CallbackQuery) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Print foobar", callback_data="print_foobar")
    keyboard.button(text="Go to Level 1", callback_data="go_to_level_1")
    await callback_query.message.edit_text("You are at Level 2", reply_markup=keyboard.as_markup())
    await callback_query.answer()


async def print_foobar_handler(callback_query: CallbackQuery) -> None:
    await callback_query.answer("foobar")


async def go_to_level_1_handler(callback_query: CallbackQuery) -> None:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Go to Level 2", callback_data="go_to_level_2")
    await callback_query.message.edit_text("You are at Level 1", reply_markup=keyboard.as_markup())
    await callback_query.answer()


async def main() -> None:
    # - Init deps

    deps = Deps.load()

    # - Initialize Bot instance with default bot properties which will be passed to all API calls

    dp = Dispatcher()  # All handlers should be attached to the Router (or Dispatcher)

    # - Register handlers

    dp.message.register(command_start_handler, CommandStart())
    dp.callback_query.register(level_2_handler, F.data == "go_to_level_2")
    dp.callback_query.register(print_foobar_handler, F.data == "print_foobar")
    dp.callback_query.register(go_to_level_1_handler, F.data == "go_to_level_1")

    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Go to Level 2", callback_data="go_to_level_2")
    print(keyboard.as_markup())
    # - Start polling

    await dp.start_polling(
        Bot(
            token=deps.config.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
