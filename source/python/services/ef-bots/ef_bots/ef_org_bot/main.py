import asyncio
import random
import textwrap

from typing import Callable, Optional, Tuple

from aiogram.types import BotCommand
from ef_bots.ef_org_bot.add_user_to_chats import add_user_to_chats
from ef_bots.ef_org_bot.deps.deps import Deps
from teletalk.app import App
from teletalk.blocks.menu import Menu, go_back, go_forward, go_to_root
from teletalk.blocks.simple_block import SimpleBlock
from teletalk.models.response import Response
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import User


def menu(deps: Deps):
    async def start_onboarding(response: Response):
        # - Ask for telegram username

        while True:
            # - Ask for telegram username

            telegram_username = await response.ask("Введи телегу участника:")
            telegram_username = telegram_username.replace("@", "").replace("t.me/", "").replace("https://t.me/", "")

            # - Get user entity

            try:
                entity = await deps.telegram_user_client.get_entity(f"@{telegram_username}")
            except:
                entity = None

            if isinstance(entity, User):
                answer = await response.ask(
                    f"t.me/{telegram_username}",
                    inline_keyboard=[["✅ Все верно!", "❌ Я ошибся"]],
                )
                await response.tell(f"t.me/{telegram_username}", mode="inplace")
                if answer == "✅ Все верно!":
                    break
            else:
                await response.tell("Не нашел такого пользователя")

        # - Add to all telegram ecosystem: ef channel, ef random coffee

        user = await deps.telegram_user_client.get_entity(f"@{telegram_username}")

        # await add_user_to_chats(
        #     telegram_client=deps.telegram_user_client,
        #     username=telegram_username,
        #     chats=deps.config.telegram_ef_chats.values(),
        # )

        await response.tell(f"Добавил во все чаты и каналы: {', '.join(deps.config.telegram_ef_chats.keys())}")

        await response.tell("Создаю страницы в Notion...")

        # - Get full name

        full_name = f"{user.first_name} {user.last_name}"

        # - Create notion page in CRM

        # -- Create page

        result, new_pages = await deps.notion_client().upsert_database(
            database={
                "id": "4675fa21409b4f46b29946279040ba96",  # pragma: allowlist secret
            },
            pages=[{"properties": {"Name": {"title": [{"text": {"content": full_name}}]}}}],
            page_unique_id_func=lambda page: page["properties"]["Name"]["title"][0]["text"]["content"],
        )

        # -- Find page

        await response.tell(f"Создал новую страницу в CRM: {new_pages[0]['url']}")

        # - Create onboarding page in EF

        # -- Create personal page if not exists

        page = await deps.notion_client().upsert_page(
            page={
                "parent": {
                    "page_id": "5caeefe3bf5645b39b0995f02fc55b82",  # персональные пространства
                },
                "properties": {"title": {"title": [{"text": {"content": full_name}}]}},
            },
        )

        # -- Create onboarding page

        onboarding_page = await deps.notion_client().duplicate_page(
            page_id="8c93fa8355344cbd88544b3a076ef552",  # Шаблон онбординга, https://www.notion.so/8c93fa8355344cbd88544b3a076ef552
            destination_page_id=page["id"],  # https://www.notion.so/5caeefe3bf5645b39b0995f02fc55b82
        )

        # pick random emoji

        await deps.notion_client().pages.update(page_id=onboarding_page["id"], icon={"type": "emoji", "emoji": "🏄‍♂️"})

        # -- Set emoji for page

        await response.tell(f"Создал страницу для онбоардинга: {onboarding_page['url']}")
        await response.tell(
            "Возьми у участника email в Notion и пошарь ему страницу Home в Notion: https://www.notion.so/Home-23bdeeca8c8e4cd99a90f67ea497c5c0?pvs=4"
        )
        await response.tell(
            f"После этого перешли ему ссылку на онбоардинг, чтобы он заполнил: {onboarding_page['url']}"
        )
        await response.tell("Поставь себе напоминалки, чтобы убедиться, что он все заполнил")

        # - Return to main menu

        return await response.ask()

    return Menu(
        "Выбери действие:",
        grid=[
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
            commands=[BotCommand(command="start", description="Start the bot")],
        ).start_polling()

    asyncio.run(main())


if __name__ == "__main__":
    test()
