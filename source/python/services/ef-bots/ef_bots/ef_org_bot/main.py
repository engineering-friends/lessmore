import asyncio
import random
import textwrap

from typing import Callable, Optional, Tuple

from aiogram.types import BotCommand
from diskcache.core import full_name
from ef_bots.ef_org_bot.add_user_to_chats import add_user_to_chats
from ef_bots.ef_org_bot.deps.deps import Deps
from loguru import logger
from teletalk.app import App
from teletalk.blocks.simple_block import SimpleBlock
from teletalk.models.response import Response
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import User


def menu(deps: Deps):
    async def start_onboarding(response: Response):
        # - Cancel callback to exit early

        async def cancel_callback(response: Response):
            if response.block_messages[-1].text == "/cancel":
                return "/cancel"
            elif response.block_messages[-1].text:
                return await response.ask(mode="inplace")  # ask again, this won't do

        # - 1. Notion access

        answer = await response.ask(
            "1. Для начала тебе нужно пошарить участнику доступ в Notion: [Home](https://www.notion.so/Home-23bdeeca8c8e4cd99a90f67ea497c5c0?pvs=4)",
            inline_keyboard=[["✅ Готово"]],
            message_callback=cancel_callback,
        )

        if answer == "/cancel":
            return await response.ask()

        # - 2. Add to all telegram ecosystem: ef channel, ef random coffee,

        while True:
            # - Ask for telegram username

            answer = await response.ask("2. Введи телеграм участника, чтобы я добавил его в чаты и каналы:")

            if answer == "/cancel":
                return await response.ask()

            telegram_username = answer.replace("@", "").replace("t.me/", "").replace("https://t.me/", "")

            # - Get user entity

            try:
                entity = await deps.telegram_user_client.get_entity(f"@{telegram_username}")
            except:
                entity = None

            if isinstance(entity, User):
                answer = await response.ask(
                    f"t.me/{telegram_username}",
                    inline_keyboard=[["✅ Все верно", "❌ Я ошибся"]],
                )

                if answer == "/cancel":
                    return await response.ask()

                await response.tell(f"t.me/{telegram_username}", mode="inplace")

                if answer == "✅ Все верно":
                    break
            else:
                await response.tell("Не нашел такого пользователя")

        # - Add to all telegram ecosystem: ef channel, ef random coffee

        user = await deps.telegram_user_client.get_entity(f"@{telegram_username}")

        answer = await response.ask(
            "Добавить пользователя в наши чаты и каналы?",
            inline_keyboard=[["✅ Да", "❌ Нет"]],
            message_callback=cancel_callback,
        )

        if answer == "/cancel":
            return await response.ask()

        if answer == "✅ Да":
            try:
                await add_user_to_chats(
                    telegram_client=deps.telegram_user_client,
                    username=telegram_username,
                    chats=deps.config.telegram_ef_chats.values(),
                )
                await response.tell(f"Добавил в чаты и каналы: {', '.join(deps.config.telegram_ef_chats.keys())}")
            except Exception as e:
                logger.error("Failed to add user to chats", error=e)
                await response.tell(f"Не удалось добавить пользователя в часть чатов и каналов. Ошибка: {str(e)}")

        # - 3. Get full name

        telegram_full_name = f"{user.first_name} {user.last_name}"
        answer = await response.ask(
            "3. Введи полное имя участника (на любом языке)",
            inline_keyboard=[[f"✏️ Взять из телеги: {telegram_full_name}"]],
        )

        if answer == "/cancel":
            return await response.ask()

        full_name = telegram_full_name if "✏️" in answer else answer

        # - 4. Create onboarding page in Notion

        # -- Prompt

        await response.tell("4. Создаю страницу онбординга в Notion, если ее еще нет. Перешли ее участнику")

        # -- Create page

        result, new_pages = await deps.notion_client().upsert_database(
            database={
                "id": "106b738eed9a80cf8669e76dc12144b7",  # pragma: allowlist secret
            },
            pages=[{"properties": {"Name": {"title": [{"text": {"content": full_name}}]}}}],
            page_unique_id_func=lambda page: page["properties"]["Name"]["title"][0]["text"]["content"],
        )

        # -- Fill the template

        await asyncio.sleep(0.5)

        await response.tell(
            f"Твоя страница онбординга: [онбординг {full_name}]({new_pages[0]['url']}). Заполни ее, там все расписано!"
        )

        await asyncio.sleep(1)

        # - 5. Write a final message

        await response.ask(
            "5. Убедись, чтобы он все сделал. Как сделает, Матвей увидит и напишет пост о новом участнике, а также поможет ему сделать его первый запрос. На этом онбординг будет завершен",
            inline_keyboard=[["✅ Завершить"]],
        )

        return await response.ask()

    return SimpleBlock(
        "⚙️ *Выбери действие*",
        inline_keyboard=[
            [("Заонбордить участника", start_onboarding)],
            [("Notion EF Org", "https://www.notion.so/Org-48f403a0d3014dc4972f08060031308e?pvs=4")],
            [("Стратегия и задачи", "https://www.notion.so/f3f7637c9a1d4733a4d90b33796cf78e?pvs=4")],
            [("Тексты кандидатам", "https://www.notion.so/EF-f1c2d3aeceb04272a61beb6c08c92b47?pvs=4")],
        ],
    )


def test():
    async def main():
        # - Init deps

        deps = Deps.load()

        # - Start user

        await deps.telegram_user_client.start()

        # # - Start bot

        await App(
            bot=deps.config.telegram_bot_token,
            command_starters={"/start": lambda response: response.ask(menu(deps))},
            commands=[
                BotCommand(command="start", description="Start the bot"),
                BotCommand(command="cancel", description="Cancel the current operation"),
            ],
        ).start_polling()

    asyncio.run(main())


if __name__ == "__main__":
    test()
