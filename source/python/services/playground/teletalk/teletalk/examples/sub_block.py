import asyncio
import random

from typing import Callable

from aiogram.types import InlineKeyboardMarkup
from teletalk.app import App
from teletalk.blocks.simple_block import SimpleBlock
from teletalk.models.block import Block
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


class TwoButtons(Block):
    def __init__(self, buttons: list[SimpleBlock]):
        super().__init__()
        self.children = buttons

    def output(self) -> BlockMessage:
        return BlockMessage(
            text="/".join([button.text for button in self.children]),
            inline_keyboard_markup=InlineKeyboardMarkup(
                inline_keyboard=sum(
                    [button.output().inline_keyboard_markup.inline_keyboard for button in self.children], []
                ),
            ),
        )


async def starter(response: Response):
    async def on_click(response: Response):
        response.prompt_sub_block.text += random.choice(["!", "1"])
        return await response.ask()

    return await response.ask(
        TwoButtons(
            buttons=[
                SimpleBlock(text="Button1", inline_keyboard_markup=[[("Click me!", on_click)]]),
                SimpleBlock(text="Button2", inline_keyboard_markup=[[("No, click me!", on_click)]]),
            ]
        ),
        mode="inplace_by_id",
    )


def test():
    asyncio.run(
        App(
            bot=TestDeps.load().config.telegram_bot_token,
            message_starter=starter,
        ).start_polling()
    )


if __name__ == "__main__":
    test()
