import asyncio
import random

from aiogram.types import InlineKeyboardMarkup
from teletalk.app import App
from teletalk.blocks.block import Block
from teletalk.models.base_block import BaseBlock
from teletalk.models.block_message import BlockMessage
from teletalk.models.response import Response
from teletalk.test_deps.test_deps import TestDeps


class TwoButtons(BaseBlock):
    def __init__(self, buttons: list[Block]):
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
        return await response.ask(mode="inplace")

    return await response.ask(
        TwoButtons(
            buttons=[
                Block(text="Button1", inline_keyboard=[[("Click me!", on_click)]]),
                Block(text="Button2", inline_keyboard=[[("No, click me!", on_click)]]),
            ]
        ),
    )


def test():
    deps = TestDeps.load()
    asyncio.run(
        App().run(
            bot=deps.config.telegram_bot_token,
            starters={deps.config.telegram_test_chat_id: starter},
            message_starter=starter,
        )
    )


if __name__ == "__main__":
    test()
