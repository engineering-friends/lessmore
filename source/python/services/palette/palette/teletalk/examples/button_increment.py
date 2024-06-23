import asyncio

from aiogram.types import Message
from palette.deps import Deps
from palette.teletalk.context.interaction import Talk
from palette.teletalk.elements.element import Element
from palette.teletalk.elements.lib.button_element import ButtonElement
from palette.teletalk.start_polling.start_polling import start_polling


async def command_starter(message: Message, interaction: Talk) -> None:
    async def _callback(message: Message, root: Element, element: ButtonElement):
        element.text = str(int(element.text) + 1)
        await message.answer("Incremented by 1")
        return await root(interaction=interaction)

    async def _message_callback(message: Message, root: Element):
        root.text = str(int(root.text) + 10)
        await message.answer("Incremented by 10")
        return await root(interaction=interaction)

    await ButtonElement(text="0", callback=_callback, message_callback=_message_callback)(
        interaction=interaction, inplace=False
    )


def test():
    asyncio.run(start_polling(command_starters={"/start": command_starter}, bot=Deps.load().config.telegram_bot_token))


if __name__ == "__main__":
    test()
