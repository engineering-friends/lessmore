from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


async def start_polling(
    bot: Bot | str,
    command_handlers: dict,
    default_bot_properties: DefaultBotProperties = DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
) -> None:
    # - Init dispatcher

    dp = Dispatcher()

    # - Register handlers

    for command, handler in command_handlers.items():
        dp.message.register(handler, command)

    # - Init bot from token if needed

    if isinstance(bot, str):
        bot = Bot(
            token=bot,
            default=default_bot_properties,
        )

    # - Start polling

    await dp.start_polling(bot=bot)
