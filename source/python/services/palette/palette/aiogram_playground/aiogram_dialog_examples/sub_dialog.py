import asyncio
import logging
import os

from typing import Any

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Data, Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.tools import render_preview, render_transitions
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Group, Next, Row, Start
from aiogram_dialog.widgets.text import Const, Format, Multi
from palette.deps.init_deps import init_deps


# name input dialog
class NameSG(StatesGroup):
    input = State()
    confirm = State()


async def name_handler(
    message: Message,
    widget: MessageInput,
    manager: DialogManager,
):
    manager.dialog_data["name"] = message.text
    await manager.next()


async def get_name_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": dialog_manager.dialog_data.get("name"),
    }


async def on_finish(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    await manager.done({"name": manager.dialog_data["name"]})


name_dialog = Dialog(
    Window(
        Const("What is your name?"),
        Cancel(),
        MessageInput(name_handler),
        state=NameSG.input,
        preview_add_transitions=[Next()],  # hint for graph rendering
    ),
    Window(
        Format("Your name is `{name}`, it is correct?"),
        Row(
            Back(Const("No")),
            Button(Const("Yes"), id="yes", on_click=on_finish),
        ),
        state=NameSG.confirm,
        getter=get_name_data,
        preview_add_transitions=[Cancel()],  # hint for graph rendering
        preview_data={"name": "John Doe"},  # for preview rendering
    ),
)


# main dialog
class MainSG(StatesGroup):
    main = State()


async def process_result(
    start_data: Data,
    result: Any,
    manager: DialogManager,
):
    if result:
        manager.dialog_data["name"] = result["name"]


async def get_main_data(dialog_manager: DialogManager, **kwargs):
    return {
        "name": dialog_manager.dialog_data.get("name"),
    }


async def on_reset_name(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    del manager.dialog_data["name"]


main_menu = Dialog(
    Window(
        Multi(
            Format("Hello, {name}", when="name"),
            Const("Hello, unknown person", when=~F["name"]),
        ),
        Group(
            Start(Const("Enter name"), id="set", state=NameSG.input),
            Button(
                Const("Reset name"),
                id="reset",
                on_click=on_reset_name,
                when="name",
                # Alternative F['name']
            ),
        ),
        state=MainSG.main,
        getter=get_main_data,
        preview_data={"name": "John Doe"},  # for preview rendering
    ),
    on_process_result=process_result,
)

dialog_router = Router()
dialog_router.include_router(name_dialog)
dialog_router.include_router(main_menu)


async def start(message: Message, dialog_manager: DialogManager):
    # it is important to reset stack because user wants to restart everything
    await dialog_manager.start(MainSG.main, mode=StartMode.RESET_STACK)


async def main():
    # - Init deps

    deps = init_deps()

    # - Init dispatcher

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(dialog_router)
    dp.message.register(start, CommandStart())
    render_transitions(dp)
    await render_preview(dp, "preview.html")
    setup_dialogs(dp)

    # - Start polling

    await dp.start_polling(Bot(token=deps.config.telegram_bot_token))


if __name__ == "__main__":
    asyncio.run(main())
