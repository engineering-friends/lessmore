import asyncio

from aiogram.types import CallbackQuery, Message
from palette.deps.init_deps import init_deps
from palette.teledo.elements import ButtonElement, Element, run_element
from palette.teledo.start_polling import start_polling


async def start(message: Message) -> None:
    await message.answer(f"Hello, Mark Lidenberg!")

    async def _callback(callback_query: CallbackQuery, root: Element, node: Element):
        node.text = str(int(node.text) + 1)
        return await run_element(element=root, message=callback_query.message)

    print(
        "Result",
        await run_element(
            element=ButtonElement(text="0", callback=_callback),
            message=message,
            inplace=False,
        ),
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
