import asyncio

from palette.deps import Deps
from palette.teletalk.crowd.response import Response
from palette.teletalk.start_polling import start_polling


async def return_text(response: Response) -> None:
    return response.message.text


async def echo(response: Response) -> None:
    await response.tell.answer(response.message.text)
    years = await response.ask(message_callback=return_text)
    await response.tell.answer(f"You are {years} years old")


def test():
    asyncio.run(
        start_polling(
            message_starter=echo,
            bot=Deps.load().config.telegram_bot_token,
        )
    )


if __name__ == "__main__":
    test()
