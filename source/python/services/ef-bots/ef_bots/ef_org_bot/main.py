import asyncio

from typing import Callable, Optional, Tuple

from ef_bots.ef_org_bot.deps.deps import Deps
from teletalk.app import App
from teletalk.blocks.menu import Menu, go_back, go_forward, go_to_root
from teletalk.models.response import Response
from telethon.tl.functions.channels import InviteToChannelRequest


def menu(deps: Deps):
    async def start_onboarding(response: Response):
        # - Ask for name

        name = await response.ask("Как зовут?")

        # - Ask for telegram username

        telegram_username = await response.ask("Ник в телеге")
        telegram_username = telegram_username.replace("@", "")

        # - Add to all telegram ecosystem: ef channel, ef random coffee

        # Get the channel and user objects
        user = await deps.telegram_user_client.get_entity(f"@{telegram_username}")
        await deps.telegram_user_client(
            InviteToChannelRequest(
                channel=await deps.telegram_user_client.get_entity(deps.config.telegram_ef_channel), users=[user]
            )
        )

        await response.tell("Добавил в канал EF Channel")

        # - Create notion page for the user, if not exists

        # - Return to main menu

        return await response.ask()

    return Menu(
        "Выбери действие:",
        grid=[[("Заонбордить участника", start_onboarding)]],
    )


def test():
    async def main():
        # - Init deps

        deps = Deps.load()

        # - Start user

        await deps.telegram_user_client.start()

        async for dialog in deps.telegram_user_client.iter_dialogs():
            print(dialog.title, dialog.id)
        # # - Start bot
        #
        # await App(
        #     bot=deps.config.telegram_bot_token,
        #     command_starters={"/start": lambda response: response.ask(menu(deps))},
        # ).start_polling()

    asyncio.run(main())


if __name__ == "__main__":
    test()
