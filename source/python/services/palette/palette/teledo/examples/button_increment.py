import asyncio

from aiogram.types import Message
from palette.deps import Deps
from palette.teledo.context.interaction import Interaction
from palette.teledo.elements.element import Element
from palette.teledo.elements.lib.button_element import ButtonElement
from palette.teledo.start_polling.start_polling import start_polling


async def command_starter(message: Message, interaction: Interaction) -> None:
    async def _callback(message: Message, root: Element, element: ButtonElement):
        element.text = str(int(element.text) + 1)
        return await root(interaction=interaction)

    await ButtonElement(text="0", callback=_callback)(interaction=interaction, inplace=False)


def test():
    asyncio.run(start_polling(command_starters={"/start": command_starter}, bot=Deps.load().config.telegram_bot_token))


if __name__ == "__main__":
    test()
