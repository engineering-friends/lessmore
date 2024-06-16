"""A checkbox form for target names selection."""

from telegram_poweruser.mini_apps.channeled_sharing.imports.runtime import *  # isort: skip

# - Helpers


def _build_keyboard(available_options, selected_options) -> InlineKeyboardMarkup:
    """Helper function to build the next inline keyboard.

    Available options + ✓ Готово.
    """

    return InlineKeyboardMarkup.from_column(
        [
            InlineKeyboardButton(
                ("✅ " if option in selected_options else "") + option, callback_data=(option, selected_options)
            )
            for option in available_options
        ]
        + [InlineKeyboardButton("✓ Готово", callback_data=("✓ Готово", selected_options))]
    )


# - Bot commands


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Start command received")

    # - Process simple start command

    if not (
        isinstance(shared_memory["names_selector"].get("names"), list)
        and isinstance(shared_memory["names_selector"].get("pre_selected_names"), list)
        and set(shared_memory["names_selector"]["pre_selected_names"]).issubset(
            set(shared_memory["names_selector"]["names"])
        )
    ):
        await update.message.reply_text(text="Для использования бота пошлите сообщение в канал топика")
        return

    # - Process form (will be called from the bot itself)

    await update.message.reply_text(
        text="Сформируйте рассылку (выборка по прошлой сессии)"
        if shared_memory["names_selector"]["pre_selected_source"] == "last_topic_message"
        else "Сформируйте рассылку (случайная выборка)",
        reply_markup=_build_keyboard(
            available_options=list(shared_memory["names_selector"]["names"]),
            selected_options=list(shared_memory["names_selector"]["pre_selected_names"]),
        ),
    )


async def name_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Name button pressed")

    # - Get answer

    query = update.callback_query
    await query.answer()
    option, selected_options = cast(Tuple[str, List[str]], query.data)

    # - Add/remove from selected options

    if option in selected_options:
        selected_options.remove(option)
    else:
        selected_options.append(option)

    # - Update form

    await query.edit_message_reply_markup(
        reply_markup=_build_keyboard(
            available_options=shared_memory["names_selector"]["names"], selected_options=selected_options
        ),
    )

    # - Drop callback data

    context.drop_callback_data(query)


async def ready_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Ready button pressed")

    # - Get answer

    query = update.callback_query
    await query.answer()
    option, selected_options = cast(Tuple[str, List[str]], query.data)

    # - Sort alphabetically

    selected_options = list(sorted(selected_options))

    # - Form list

    """
    Рассылка: 
    - Сима 
    - Папа 
    ...
    - Мама 
    
    """
    await query.edit_message_text("Рассылка:\n{}".format("\n".join([f" - {name}" for name in selected_options])))

    # - Save to shared memory

    shared_memory["names_selector"]["selected_names"] = selected_options

    # - Drop callback data

    context.drop_callback_data(query)


# - Build application


def build_application():
    logger.info("Building bot application")

    # - Create directories if needed

    if not os.path.exists("data/dynamic/"):
        os.makedirs("data/dynamic/")

    # - Build app

    application = (
        Application.builder()
        .token(config.telegram_bot_token)
        .persistence(PicklePersistence(filepath=os.path.join("data/dynamic/", os.path.basename(__file__)[:-3])))
        .arbitrary_callback_data(True)
        .build()
    )

    # - Add handlers

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(name_button, pattern=lambda value: value[0] != "✓ Готово"))
    application.add_handler(CallbackQueryHandler(ready_button, pattern=lambda value: value[0] == "✓ Готово"))

    # - Return

    return application
