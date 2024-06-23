import asyncio

from aiogram.types import Message
from palette.deps import Deps
from palette.teletalk.crowd.talk import Talk
from palette.teletalk.elements.element import Element
from palette.teletalk.elements.lib.button_element import ButtonElement
from palette.teletalk.start_polling.start_polling import start_polling


async def command_starter(message: Message, talk: Talk) -> None:
    async def _callback(message: Message, root: Element, element: ButtonElement):
        root.text = str(int(root.text) + 1)
        await message.answer("Incremented by 1")
        return await root(talk=talk)

    await ButtonElement(text="0", callback=_callback, message_callback=_callback)(talk=talk, inplace=False)


def test():
    asyncio.run(start_polling(command_starters={"/start": command_starter}, bot=Deps.load().config.telegram_bot_token))


if __name__ == "__main__":
    test()
