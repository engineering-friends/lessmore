import asyncio
import textwrap

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from ef_bots.ef_main_bot.deps import Deps
from ef_matchmaking_bot.handlers_proper.send_ef_post.send_ef_post import send_ef_post
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
    from ef_bots.ef_main_bot.tests.test_write_post import test_write_post


media_types = [
    ("photo", lambda m: m.photo[-1] if m.photo else None),
    # todo maybe: implement
    # ("video", lambda m: m.video),
    # ("document", lambda m: m.document),
    # ("audio", lambda m: m.audio),
    # ("voice", lambda m: m.voice),
    # ("sticker", lambda m: m.sticker),
    # ("animation", lambda m: m.animation),
]


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
                EfMainBot(deps=deps),  # this class
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

        # -- Generate with AI

        title_ai = "diddle doo"

        title = await response.ask(
            "2. Введи заголовок поста",
            inline_keyboard=[[f"🤖 Взять наш вариант: {title_ai}"]],
            message_callback=handle_cancel_callback,
        )

        # - 4. Validate the post

        should_generate_new_cover = True  # start fresh

        while True:
            # - Send the post to the bot first, to validate it

            await send_ef_post(
                title=title,
                author_name=response.message.from_user.full_name,
                body=response.message.html_text,
                file_ids=[
                    file_id
                    for _, get_media in media_types
                    for message in response.messages
                    if (file_id := getattr(get_media(message), "file_id", ""))
                ],  # note: only photos are supported for now
                chat_id=response.chat_id,
                bot=response.talk.app.bot,
                notion_token=self.deps.config.notion_token,
                tags=[],
            )

            if should_generate_new_cover:
                should_generate_new_cover = False

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
                    inline_keyboard=[[f"🤖 Взять наш вариант: {title_ai}"]],
                )
            elif answer == "✏️ Поменять текст":
                body = await response.ask("Введи новый текст поста")
                title_ai = "diddle doo-2"
            elif answer == "🖼️ Другую картинку":
                should_generate_new_cover = True

        # - 5. Send the post to the channel

        await send_ef_post(
            title=title,
            author_name=response.message.from_user.full_name,
            body=response.message.html_text,
            file_ids=[
                file_id
                for _, get_media in media_types
                for message in response.messages
                if (file_id := getattr(get_media(message), "file_id", ""))
            ],  # note: only photos are supported for now
            chat_id=160773045,  # mark lidenberg
            bot=response.talk.app.bot,
            notion_token=self.deps.config.notion_token,
            tags=[],
        )
