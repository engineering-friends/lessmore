import asyncio
import io
import os
import textwrap
import uuid

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from ef_bots.ef_main_bot.deps import Deps
from ef_matchmaking_bot.handlers_proper.send_ef_post.ai.generate_article_cover import generate_article_cover
from ef_matchmaking_bot.handlers_proper.send_ef_post.get_notion_user_properties import get_notion_user_properties
from ef_matchmaking_bot.handlers_proper.send_ef_post.send_ef_post import send_ef_post
from lessmore.utils.asynchronous.async_retry import async_retry
from lessmore.utils.cache_on_disk import cache_on_disk
from lessmore.utils.file_primitives.ensure_path import ensure_path
from lessmore.utils.file_primitives.write_file import write_file
from lessmore.utils.tested import tested
from loguru import logger
from PIL.Image import Image
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

cache_dir = os.path.join(os.path.dirname(__file__), ".cache/")


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
        await response.tell(
            "Я соберу у тебя всю необходимую информацию для поста, дам на проверку, и затем отправлю его в EF Channel"
        )

        # - 1. Write post

        body_response = await response.ask(
            "1. Напиши содержание поста + приложи картинки, если нужно. Пока без заголовка",
            message_callback="raw",
        )

        # - Unpack data from the response

        face_message = body_response.messages[0]
        file_ids = [
            file_id
            for _, get_media in media_types
            for message in body_response.messages
            if (file_id := getattr(get_media(message), "file_id", ""))
        ]

        # - 2. Get title

        # -- Generate with AI

        title_ai = "diddle doo"

        title = await response.ask(
            "2. Введи заголовок поста",
            inline_keyboard=[[f"🤖 Взять наш вариант: {title_ai}"]],
            message_callback=handle_cancel_callback,
        )

        if "🤖" in title:
            title = title_ai

        # - 4. Validate the post

        should_generate_new_cover = not file_ids

        while True:
            # - Send the post to the bot first, to validate it

            await response.tell("Подготавливаю пост...")

            await send_ef_post(
                title=title,
                author_name=face_message.from_user.full_name,
                body=face_message.html_text,
                file_ids=file_ids,  # note: only photos are supported for now
                chat_id=response.chat_id,
                bot=response.talk.app.bot,
                notion_token=self.deps.config.notion_token,
                reset_image_cache=should_generate_new_cover,
                tags=[],
                reaction_probability=0,
            )

            # - Disable generating new cover after one has been generated

            should_generate_new_cover = False

            # - Ask if the post is valid

            answer = await response.ask(
                "⚙️ Все ок?",
                inline_keyboard=[
                    ["✅ Все ок!"],
                    ["✏️ Поменять название"],
                    ["✏️ Поменять текст"],
                ]
                + ([["🖼️ Другую картинку"]] if not file_ids else []),
            )

            if answer == "✅ Все ок!":
                # go forward
                break
            elif answer == "✏️ Поменять название":
                title = await response.ask(
                    "Введи новый заголовок поста",
                    inline_keyboard=[[f"🤖 Взять наш вариант: {title_ai}"]],
                    message_callback=handle_cancel_callback,
                )
                if "🤖" in title:
                    title = title_ai

            elif answer == "✏️ Поменять текст":
                body = await response.ask("Введи новый текст поста")
                title_ai = "diddle doo-2"
            elif answer == "🖼️ Другую картинку":
                should_generate_new_cover = True

        # - Notify user that the post was sent

        await response.tell("Отправляю пост в канал...")

        # - 5. Send the post to the channel

        message = await send_ef_post(
            title=title,
            author_name=face_message.from_user.full_name,
            body=face_message.html_text,
            file_ids=file_ids,  # note: only photos are supported for now
            chat_id=160773045,  # mark lidenberg
            bot=response.talk.app.bot,
            notion_token=self.deps.config.notion_token,
            tags=[],
        )

        await response.tell("Готово!")
