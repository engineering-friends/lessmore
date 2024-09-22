import asyncio
import textwrap

from aiogram.types import BotCommand
from ef_bots.ef_org_bot.add_user_to_chats import add_user_to_chats
from ef_bots.ef_org_bot.deps.deps import Deps
from loguru import logger
from more_itertools import last
from pymaybe import maybe
from rocksdict import Rdict
from teletalk.app import App
from teletalk.blocks.simple_block import CancelError, SimpleBlock, build_default_message_callback
from teletalk.models.response import Response
from telethon.tl.types import User


"""
Ideas: 
- Send reminders for the user to check if the member has filled the form
- Send messages to the member? 
"""


def build_main_menu(deps: Deps):
    async def start_onboarding(response: Response):
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
                entity = await deps.telegram_user_client.get_entity(f"@{telegram_username}")
            except:
                entity = None

            # - If user if found and it's correct, break the loop

            if isinstance(entity, User):
                answer = await response.ask(
                    f"t.me/{telegram_username}",
                    inline_keyboard=[["✅ Все верно", "❌ Я ошибся"]],
                )

                if answer == "✅ Все верно":
                    break
            else:
                await response.tell("Не нашел такого пользователя")

        # -- Get user

        user = await deps.telegram_user_client.get_entity(f"@{telegram_username}")

        # -- Add user to chats

        answer = await response.ask(
            "Добавить пользователя в наши чаты и каналы?",
            inline_keyboard=[["✅ Да", "❌ Нет"]],
        )

        if answer == "✅ Да":
            try:
                await add_user_to_chats(
                    telegram_client=deps.telegram_user_client,
                    username=telegram_username,
                    chats=list(deps.config.telegram_ef_chats.values()),
                )
                await response.tell(f"Добавил в чаты и каналы: {', '.join(deps.config.telegram_ef_chats.keys())}")
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

        result, new_pages = await deps.notion_client().upsert_database(
            database={
                "id": "106b738eed9a80cf8669e76dc12144b7",  # pragma: allowlist secret
            },
            pages=[{"properties": {"Name": {"title": [{"text": {"content": f"🏄‍♂️ Онбординг в EF для {full_name}"}}]}}}],
            page_unique_id_func=lambda page: page["properties"]["Name"]["title"][0]["text"]["content"],
        )

        # -- Fill the template

        await asyncio.sleep(0.5)

        await response.tell(
            textwrap.dedent(f"""
⚙️ Добро пожаловать в EF! 

На данный момент мы тебя добавили:
- В наш [Notion](https://www.notion.so/Home-23bdeeca8c8e4cd99a90f67ea497c5c0?pvs=4) 
- В наш канал EF Channel. Там у нас все посты и запросы - в том числе твои будут
- В чатик EF Random Coffee - там основные знакомства, участвуй! :)

Для онбординга нужно заполнить страничку в Notion: [🏄‍♂️ Онбординг в EF для {full_name}]({new_pages[0]['url']})
""")
        )

        await asyncio.sleep(0.5)

        # - 5. Write a final message

        # -- Send a reminder in 3 days  to check if the user has filled the form

        # todo later:  [@marklidenberg]

        # -- Send the final message for the user

        await response.ask(
            "5. Последний шаг - убедиться, чтобы участник все заполнил! Как сделает, Матвею придет уведомление, после чего он напишет о нем пост и поможет ему сделать его первый запрос. На этом онбординг будет завершен, мерси боку! ",
            inline_keyboard=[["✅ Завершить"]],
        )

        return await response.ask()

    async def safe_start_onboarding(response: Response):
        try:
            return await start_onboarding(response)
        except CancelError:
            return await response.ask()
        except Exception as e:
            logger.exception("Failed to start onboarding", error=e)
            await response.tell(f"Ошибка во время процесса онбординга: {str(e)}")
            return await response.ask()

    return SimpleBlock(
        "⚙️ *Выбери действие*",
        inline_keyboard=[
            [("Заонбордить участника", safe_start_onboarding)],
            [("Notion EF Org", "https://www.notion.so/Org-48f403a0d3014dc4972f08060031308e?pvs=4")],
            [("Стратегия и задачи", "https://www.notion.so/f3f7637c9a1d4733a4d90b33796cf78e?pvs=4")],
            [("Тексты кандидатам", "https://www.notion.so/EF-f1c2d3aeceb04272a61beb6c08c92b47?pvs=4")],
        ],
        message_callback=lambda response: response.ask(mode="inplace"),
    )


def main(env="test"):
    async def _main():
        # - Init deps

        deps = Deps.load(env=env)

        # - Start user

        await deps.telegram_user_client.start()

        # - Load chat_ids to run at startup - the ones which have last message from the bot (usually the menu message). Needed for user not to press /start if bot has been restarted, and just used the menu of the last message (beta)

        chat_ids_to_run_at_startup = []

        # -- Reset state if needed

        # Rdict.destroy(str(deps.local_files_dir / "app_state"))

        # -- Load state

        user_states = Rdict(path=str(deps.local_files_dir / "app_state"))
        for chat_id, user in user_states.items():
            if maybe(user)["messages"][-1]["from_user"]["is_bot"].or_else(False):
                chat_ids_to_run_at_startup.append(int(chat_id))

        user_states.close()

        logger.info("Chats to run at startup", chat_ids=chat_ids_to_run_at_startup)

        # - Run app

        await App(
            bot=deps.config.telegram_bot_token,
            initial_starters={
                chat_id: lambda response: response.ask(build_main_menu(deps), mode="inplace_latest")
                for chat_id in chat_ids_to_run_at_startup
            },  # in case of restart, we will start from the last bot message
            command_starters={"/start": lambda response: response.ask(build_main_menu(deps))},
            commands=[
                BotCommand(command="start", description="Start the bot"),
                BotCommand(command="cancel", description="Cancel the current operation"),
            ],
            persistant_state_path=str(deps.local_files_dir / "app_state"),
        ).start_polling()

    asyncio.run(_main())


if __name__ == "__main__":
    import fire

    fire.Fire(main)
