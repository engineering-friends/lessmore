import asyncio
import textwrap

from typing import TYPE_CHECKING

from aiogram.types import BotCommand
from ef_bots.ef_org_bot.add_user_to_chats import add_user_to_chats
from ef_bots.ef_org_bot.deps.deps import Deps
from lessmore.utils.tested import tested
from loguru import logger
from pymaybe import maybe
from teletalk.app import App
from teletalk.blocks.block import Block
from teletalk.blocks.build_default_message_callback import build_default_message_callback
from teletalk.blocks.handle_errors import handle_errors
from teletalk.models.response import Response
from telethon.tl.types import User


if TYPE_CHECKING:
    from ef_bots.ef_org_bot.tests.test_start_onboarding import test_start_onboarding


class EFOrgBot(Deps):
    @property
    def menu(self) -> Block:
        return Block(
            "⚙️ *Выбери действие*",
            inline_keyboard=[
                [("Заонбордить участника", self.start_onboarding)],
                [("Notion EF Org", "https://www.notion.so/Org-48f403a0d3014dc4972f08060031308e?pvs=4")],
                [("Стратегия и задачи", "https://www.notion.so/f3f7637c9a1d4733a4d90b33796cf78e?pvs=4")],
                [("Тексты кандидатам", "https://www.notion.so/EF-f1c2d3aeceb04272a61beb6c08c92b47?pvs=4")],
            ],
        )

    @tested([test_start_onboarding] if TYPE_CHECKING else [])
    @handle_errors
    async def start_onboarding(self, response: Response):
        # - 1. Notion access

        await response.ask(
            "1. Для начала тебе нужно узнать email от Notion участника и пошарить ему доступ на [Home](https://www.notion.so/Home-23bdeeca8c8e4cd99a90f67ea497c5c0?pvs=4)",
            inline_keyboard=[["✅ Доступ есть"]],
        )

        # - 2. Add to all telegram ecosystem: ef channel, ef random coffee,

        # -- Ask for telegram username

        while True:
            # - Ask for telegram username

            answer = await response.ask(
                "2. Введи телеграм участника, чтобы я добавил его в чаты и каналы (в любом формате)"
            )

            telegram_username = answer.replace("@", "").replace("https://t.me/", "").replace("t.me/", "")

            # - Get user entity

            try:
                entity = await self.telegram_user_client.get_entity(f"@{telegram_username}")
            except:
                entity = None

            # - If user if found and it's correct, break the loop

            if isinstance(entity, User):
                answer = await response.ask(
                    f"t.me/{telegram_username}", inline_keyboard=[["✅ Все верно", "❌ Я ошибся"]]
                )

                if answer == "✅ Все верно":
                    break
            else:
                await response.tell("Не нашел такого пользователя")

        # -- Get user

        user = await self.telegram_user_client.get_entity(f"@{telegram_username}")

        # -- Add user to chats

        answer = await response.ask(
            "Добавить пользователя в наши чаты и каналы?", inline_keyboard=[["✅ Да", "❌ Нет"]]
        )

        if answer == "✅ Да":
            try:
                await add_user_to_chats(
                    telegram_client=self.telegram_user_client,
                    username=telegram_username,
                    chats=list(self.config.telegram_ef_chats.values()),
                )
                await response.tell(f"Добавил в чаты и каналы: {', '.join(self.config.telegram_ef_chats.keys())}")
            except Exception as e:
                logger.exception("Failed to add user to chats", error=e)
                await response.tell(f"Не удалось добавить пользователя в часть чатов и каналов. Ошибка: {str(e)}")

        # - 3. Get full name

        telegram_full_name = f"{user.first_name} {user.last_name}"

        answer = await response.ask(
            "3. Введи полное имя участника на любом языке",
            inline_keyboard=[[f"✏️ Взять из телеги: {telegram_full_name}"]],
            message_callback=build_default_message_callback(supress_messages=False),
        )

        full_name = telegram_full_name if "✏️" in answer else answer

        # - 4. Create onboarding page in Notion

        # -- Prompt

        await response.tell("4. Перешли участнику:")

        # -- Create page

        result, new_pages = await self.notion_client().upsert_database(
            database={
                "id": "106b738eed9a80cf8669e76dc12144b7",  # pragma: allowlist secret
            },
            pages=[{"properties": {"Name": {"title": [{"text": {"content": f"🏄‍♂️ Онбординг в EF для {full_name}"}}]}}}],
            page_unique_id_func=lambda page: page["properties"]["Name"]["title"][0]["text"]["content"],
        )

        # -- Send the message to forward to the user

        await response.tell(
            textwrap.dedent(f"""
    ⚙️ Добро пожаловать в EF! 
    
    На данный момент мы тебя добавили:
    - В [Notion](https://www.notion.so/Home-23bdeeca8c8e4cd99a90f67ea497c5c0?pvs=4) 
    - В канал EF Channel. Там у нас все посты и запросы - в том числе твои будут
    - В чатик EF Random Coffee - там основные знакомства, участвуй! :)
    
    Для онбординга нужно заполнить страничку в Notion, выбрав шаблон "▶️ Начать онбординг": [🏄‍♂️ Онбординг в EF для {full_name}]({new_pages[0]['url']})
    """)
        )

        await asyncio.sleep(0.5)

        # - 5. Write the final message

        # -- Send a reminder in 3 days  to check if the user has filled the form

        # todo later: implement

        # -- Send the final message for the user

        await response.ask(
            "5. Последний шаг - убедиться, чтобы участник все заполнил! Как сделает, Матвею придет уведомление, после чего он напишет о нем пост и поможет ему сделать его первый запрос. На этом онбординг будет завершен, мерси боку! ",
            inline_keyboard=[["✅ Готово!"]],
        )

        return await response.ask()  # go back to the original response prompt, e.g. the menu