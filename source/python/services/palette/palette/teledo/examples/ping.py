import asyncio

from aiogram.types import CallbackQuery, Message
from palette.deps.init_deps import init_deps
from palette.teledo.context import Context
from palette.teledo.elements.element import Element
from palette.teledo.elements.lib.button_element import ButtonElement
from palette.teledo.elements.run_element import run_element
from palette.teledo.start_polling.start_polling import start_polling


async def start(message: Message) -> None:
    await message.answer(f"Hello, Mark Lidenberg!")

    async def _callback(message: Message, root: Element, element: ButtonElement):
        element.text = str(int(element.text) + 1)
        return await run_element(element=root, message=message)

    await run_element(
        element=ButtonElement(text="0", callback=_callback),
        message=message,
        inplace=False,
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
