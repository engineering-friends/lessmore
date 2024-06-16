from telegram_poweruser.imports.runtime import *  # isort: skip

from telegram_poweruser.mini_apps.sessions.config import config as mini_app_config


# - Telegram

telegram_client = TelegramClient(
    session=os.path.join(get_root_directory(__file__), "data/dynamic/telegram_sessions/sessions.session"),
    api_id=config.telegram_api_id,
    api_hash=config.telegram_api_hash,
    throttle_period_in_seconds=300,
    throttle_max_count=300,
)

# - Globals

my_last_messages_by_peer = {}
is_initialized = False

# - Helpers


async def add_sessions_if_needed(peer_values):
    # - Prepare arguments

    peers = [await telegram_client.cast_peer(peer) for peer in peer_values]

    logger.info("Adding sessions", peers=peers)

    # - Add chats

    added_chat_ids = await telegram_client.add_chats_to_folder(peers, mini_app_config.session_folder_title)

    # - Unmute if needed

    if added_chat_ids:
        # unmute only if added. Do not unmute if already there
        for peer in peers:
            await telegram_client.unmute_chat(peer)

    # - Return

    return added_chat_ids


async def remove_sessions_if_needed(peer_values):
    # - Prepare arguments

    peers = [await telegram_client.cast_peer(peer) for peer in peer_values]

    logger.info("Removing sessions", peer=peers)

    # - Remove sessiosn

    removed_chat_ids = await telegram_client.remove_chats_from_folder(peers, mini_app_config.session_folder_title)

    # - Mute if needed

    if removed_chat_ids:
        # mute only if removed. Do not unmute if already not in there
        for peer in peers:
            await telegram_client.mute_chat(peer)
    return removed_chat_ids


# - Core


async def groom_sessions():
    global is_initialized

    # - Cache dialogs

    async for dialog in telegram_client.iter_dialogs():
        pass

    # - Start grooming every 5 minutes

    while True:
        try:
            logger.info("Starting session grooming...")

            # - Remove all session chats on initialization

            if not is_initialized:
                logger.info("Initializing")

                # - Remove chats

                await telegram_client.remove_chats_from_folder(
                    (await telegram_client.get_dialog_filter(mini_app_config.session_folder_title)).include_peers,
                    mini_app_config.session_folder_title,
                )

                # - Set variable

                if not is_initialized:
                    logger.info("Initialization finished.")
                    is_initialized = True

            # - Get current session peers

            _include_peers = (
                await telegram_client.get_dialog_filter(mini_app_config.session_folder_title)
            ).include_peers
            current_session_peers = [await telegram_client.cast_peer(peer) for peer in _include_peers]

            # - Get dialogs (not very old, but should cover all current session peers)

            async def _condition_to_stop(cumulative_dialogs, new_dialog):
                logger.trace("Processing dialog", title=new_dialog.title)

                # - Cast

                cumulative_peers = [
                    await telegram_client.cast_peer(dialog.input_entity) for dialog in cumulative_dialogs
                ]

                # - Check if new_dialog is old

                is_old = (
                    new_dialog.message
                    and new_dialog.message.date.replace(tzinfo=None)
                    < datetime.utcnow() - to_timedelta(mini_app_config.session_period) * 2
                )

                # - Check if collected all

                is_collected_all_current_session_peers = all(peer in cumulative_peers for peer in current_session_peers)
                logger.debug(
                    "Dialog checks",
                    is_old=is_old,
                    is_collected_all_current_session_peers=is_collected_all_current_session_peers,
                )
                return is_old and is_collected_all_current_session_peers and not new_dialog.pinned

            dialogs = await telegram_client.get_dialogs_by_condition(
                archived=False, condition_to_stop=_condition_to_stop
            )

            logger.info("Got dialogs", n_dialogs=len(dialogs))

            # - Process dialogs

            for dialog in dialogs:
                logger.info("Processing dialog", dialog_title=dialog.title)

                # - Get trail

                trail = await telegram_client.get_trail_messages(dialog.input_entity, max_messages=30)
                if not trail:
                    logger.info("Empty trail", dialog_title=dialog.title)
                    continue

                # - Get my last message

                my_last_message = trail[-1]

                # - Process my last message

                await process_my_last_message(my_last_message)

            logger.info("Session grooming finisehd")

        except:
            logger.exception("Failed to groom sessions")

        # - Wait for 5 minutes

        await asyncio.sleep(60 * 5)


async def process_my_last_message(message):
    logger.info("Processing message", text=message.text, peer=message.input_chat)

    # - Check if message has no chat for some reason (can happen if chat is all-new)

    if not message.input_chat:
        return

    # - Skip not mine messages (just in case)

    if not message.out:
        return

    # - Convert message.input_chat to peer

    peer = await telegram_client.cast_peer(message.input_chat)

    # - Save message to cache

    logger.info("My last message updated", peer=peer)
    my_last_messages_by_peer[str(peer)] = message

    # - Check if session

    is_session = str(peer) in my_last_messages_by_peer and datetime.utcnow() - my_last_messages_by_peer[
        str(peer)
    ].date.replace(tzinfo=None) <= timedelta(hours=1)

    logger.info("Session status", is_session=is_session)

    # - Act accordingly

    if is_session:
        return await add_sessions_if_needed([message.input_chat])
    else:
        return await remove_sessions_if_needed([message.input_chat])


@telegram_client.on(events.NewMessage(outgoing=True))
async def on_new_message(event):
    logger.debug("on_new_message", chat_id=event.chat_id, message_id=event.id)

    if not is_initialized:
        logger.info("Not initialized yet, skipping")
        return

    await process_my_last_message(event.message)


# - Main

if __name__ == "__main__":
    logger.info("Started sessions")

    telegram_client.start(phone=config.telegram_phone)
    asyncio.get_event_loop().create_task(groom_sessions())
    telegram_client.run_until_disconnected()
