import asyncio

from aiogram.types import Message
from palette.deps import Deps
from palette.teledo.elements.element import Element
from palette.teledo.elements.lib.button_element import ButtonElement
from palette.teledo.start_polling.start_polling import start_polling


async def start(message: Message) -> None:
    async def _callback(message: Message, root: Element, element: ButtonElement):
        element.text = str(int(element.text) + 1)
        return await root(message=message)

    await ButtonElement(text="0", callback=_callback)(message=message, inplace=False)


async def main() -> None:
    await start_polling(
        bot=Deps.load().config.telegram_bot_token,
        command_handlers={
            "start": start,
        },
        message_handler=None,
    )


if __name__ == "__main__":
    asyncio.run(main())
