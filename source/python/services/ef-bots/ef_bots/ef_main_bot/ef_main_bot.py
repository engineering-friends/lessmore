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
        # - 1. Write post

        face_message = await response.ask(
            "1. Введи текст поста",
            message_callback="raw",
        )

        # - Get notion user properties

        try:
            notion_properties = await get_notion_user_properties(
                name=face_message.from_user.full_name,
                notion_token=self.deps.config.notion_token,
            )  # {'AI стиль постов': 'style of secret of kells, old paper, celtic art', 'Name': 'Mark Lidenberg', 'TG_username': 'marklidenberg', 'url': 'https://www.notion.so/Mark-Lidenberg-d5ae5f192b4c402ba014268e63aed47c', 'Заполнена': True}
        except:
            logger.error("Failed to get user notion properties")

            notion_properties = {}

        notion_ai_style = notion_properties.get("AI стиль постов")
        notion_author_url = notion_properties.get("url", "")

        # - Get file ids from the face message

        file_ids = [
            file_id
            for _, get_media in media_types
            for message in [face_message]
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

        # - 3. Generate an image cover if no images are attached, form `files`

        if not file_ids:
            try:
                # - Generate article cover

                image_contents = await cache_on_disk(ensure_path(f"{cache_dir}/generate_image"))(
                    async_retry(tries=5, delay=1)(generate_article_cover)
                )(
                    title=title,
                    body=face_message.html_text,
                    style=notion_ai_style or "Continuous lines very easy, clean and minimalist, black and white",
                )

                # - Resize image to 1280x731 (telegram max size)

                image = Image.open(io.BytesIO(image_contents))
                image_resized = image.resize((1280, 731), Image.LANCZOS)
                image_contents = io.BytesIO()
                image_resized.save(image_contents, format="PNG")
                image_contents = image_contents.getvalue()

                # - Save to tmp file and add to files

                cover_filename = f"/tmp/{uuid.uuid4()}.png"
                write_file(
                    data=image_contents,
                    filename=cover_filename,
                    as_bytes=True,
                )
            except Exception as e:
                logger.error("Failed to generate image", e=e)

                cover_filename = ""
        else:
            cover_filename = ""

        files = file_ids
        if cover_filename:
            files.append(FSInputFile(path=cover_filename))

        # - 4. Validate the post

        should_generate_new_cover = True  # start fresh

        while True:
            # - Send the post to the bot first, to validate it

            await send_ef_post(
                title=title,
                author_name=face_message.from_user.full_name,
                body=face_message.html_text,
                file_ids=[
                    file_id
                    for _, get_media in media_types
                    for message in [face_message]
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
                "⚙️ Все ок?",
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
            author_name=face_message.from_user.full_name,
            body=face_message.html_text,
            file_ids=[
                file_id
                for _, get_media in media_types
                for message in [face_message]
                if (file_id := getattr(get_media(message), "file_id", ""))
            ],  # note: only photos are supported for now
            chat_id=160773045,  # mark lidenberg
            bot=response.talk.app.bot,
            notion_token=self.deps.config.notion_token,
            tags=[],
        )
