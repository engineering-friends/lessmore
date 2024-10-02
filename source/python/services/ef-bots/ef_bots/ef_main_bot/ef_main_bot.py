import asyncio
import textwrap

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from ef_bots.ef_main_bot.add_user_to_chats import add_user_to_chats
from ef_bots.ef_main_bot.deps import Deps
from lessmore.utils.tested import tested
from loguru import logger
from teletalk.app import App
from teletalk.blocks.block import Block
from teletalk.blocks.build_default_message_callback import handle_cancel_callback
from teletalk.blocks.handle_errors import handle_errors
from teletalk.models.response import Response
from telethon.tl.types import User


if TYPE_CHECKING:
    from ef_bots.ef_main_bot import main


@tested([main] if TYPE_CHECKING else [])
class EfMainBot:
    def __init__(self, deps: Deps):
        self.deps = deps

    # - Context manager

    @staticmethod
    @asynccontextmanager
    async def stack(env: str):
        async with Deps(env=env) as deps:
            yield (
                EfOrgBot(deps=deps),  # this class
                await App(
                    bot=deps.config.telegram_bot_token,
                    state_backend="rocksdict",
                    state_config={"path": str(deps.local_files_dir / "app_state")},
                ).__aenter__(),  # teletalk app
            )

    # - Building blocks

    @property
    def menu(self) -> Block:
        return Block(
            "⚙️ *Выбери действие*",
            inline_keyboard=[
                [("Написать пост", self.write_post)],
                # [("Создать запрос", self.create_request)],
                # [("Random Coffee", self.random_coffee)],
                # [("Узнать", self.learn_more)],
            ],
        )

    @tested([test_write_post] if TYPE_CHECKING else [])
    @handle_errors
    async def write_post(self, response: Response):
        # - 1. Write post

        body = await response.ask("1. Введи текст поста")

        # - 2. Get title

        title = await response.ask(
            "2. Введи заголовок поста",
            inline_keyboard=[["🤖 Взять наш вариант: diddle doo"]],
            message_callback=handle_cancel_callback,
        )

        # - 3. Generate an article cover

        files = []

        # - 4. Validate the post

        while True:
            # - Ask if the post is valid

            answer = await response.ask(
                "",
                inline_keyboard=[
                    ["✅ Все ок!"],
                    ["✏️ Поменять название"],
                    ["✏️ Поменять текст"],
                    ["🖼️ Другую картинку"],
                ],
            )

            if answer == "✅ Все ок!":
                break
            elif answer == "✏️ Поменять название":
                title = await response.ask(
                    "Введи новый заголовок поста",
                    inline_keyboard=[["🤖 Взять наш вариант: diddle doo"]],
                )
            elif answer == "✏️ Поменять текст":
                body = await response.ask("Введи новый текст поста")
            elif answer == "🖼️ Другую картинку":
                pass

        # - 5. Send the post to the channel

        pass
