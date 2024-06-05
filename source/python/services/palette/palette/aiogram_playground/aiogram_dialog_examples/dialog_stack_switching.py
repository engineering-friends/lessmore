import asyncio
import logging
import os

from typing import Dict

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, LaunchMode, StartMode, SubManager, Window, setup_dialogs
from aiogram_dialog.widgets.kbd import Button, Checkbox, ListGroup, ManagedCheckbox, Radio, Row
from aiogram_dialog.widgets.text import Const, Format
from palette.deps.init_deps import init_deps


class DialogSG(StatesGroup):
    first = State()
    second = State()
    third = State()


async def to_second(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.switch_to(DialogSG.second)


async def go_back(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.back()


async def go_next(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.next()


dialog = Dialog(
    Window(
        Const("First"),
        Button(Const("To second"), id="sec", on_click=to_second),
        state=DialogSG.first,
    ),
    Window(
        Const("Second"),
        Row(
            Button(Const("Back"), id="back2", on_click=go_back),
            Button(Const("Next"), id="next2", on_click=go_next),
        ),
        state=DialogSG.second,
    ),
    Window(
        Const("Third"),
        Button(Const("Back"), id="back3", on_click=go_back),
        state=DialogSG.third,
    ),
)


async def start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(DialogSG.first, mode=StartMode.RESET_STACK)


async def main():
    # - Init deps

    deps = init_deps()

    # - Init dispatcher

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(dialog)
    dp.message.register(start, CommandStart())
    setup_dialogs(dp)

    # - Start polling

    await dp.start_polling(Bot(token=deps.config.telegram_bot_token))


if __name__ == "__main__":
    asyncio.run(main())
