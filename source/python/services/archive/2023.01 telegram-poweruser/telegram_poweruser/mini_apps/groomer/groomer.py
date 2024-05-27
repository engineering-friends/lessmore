from telegram_poweruser.imports.runtime import *  # isort: skip
from telegram_poweruser.mini_apps.groomer.config import config as mini_app_config


# - Clients

telegram_client = TelegramClient(
    session=os.path.join(get_root_directory(__file__), "data/dynamic/telegram_sessions/groomer.session"),
    api_id=config.telegram_api_id,
    api_hash=config.telegram_api_hash,
    throttle_period_in_seconds=300,
    throttle_max_count=300,
)


def _is_ping_needed(message):
    """Check if message needs a ping (if unresponded).

    Rule: if message does not end with . and has ? in the ending non-alphabetic characters
    """

    # - Check if message is empty

    if not message.text:
        return False

    # - Check if message does not end with . and has ? in the ending non-alphabetic characters

    # -- Strip text

    _text = message.text.strip()

    # -- Get last_extra_symbols ("foo bar?1!!!!!" -> "?1!!!!!")

    extra_symbols_pattern = r"(?:[^\w]|\d)"
    last_extra_symbols = re.search(rf"({extra_symbols_pattern}*)$", _text).groups()[0]

    # -- Get result

    result = _text[-1:] != "." and "?" in last_extra_symbols

    # - Return

    return result


async def ping_if_needed(dialog):
    logger.info("Pinging if needed", dialog_title=dialog.title)

    # - Check if not my message

    if not dialog.message.out:
        # not my message
        return

    # - Get peer dialog

    _response = await telegram_client(functions.messages.GetPeerDialogsRequest(peers=[dialog.input_entity]))
    peer_dialog = _response.dialogs[0]

    # - Check if last message is unread

    if dialog.input_entity == types.InputPeerSelf():
        # - Saved Messages (chat with self), mark as unread

        assert peer_dialog.read_outbox_max_id == 0
        is_unread = False
    else:
        # - Mark unread if last read message if not top message

        is_unread = peer_dialog.read_outbox_max_id != peer_dialog.top_message

    if not _is_ping_needed(dialog.message) and dialog.message.text != "" and not is_unread:
        # no ping message, not empty message, not unread
        return

    # - Find my last messages

    async def _condition_to_stop(current_messages, new_message):
        return not new_message.out

    last_self_messages = await telegram_client.get_recent_messages(
        dialog.input_entity, condition_to_stop=_condition_to_stop
    )

    # - Return if no new my last message

    if not last_self_messages:
        return

    # - Collect pings and last message

    last_pings = []
    last_message = None

    for message in last_self_messages:
        if message.text == "":
            # ping!
            last_pings.append(message)
        else:
            # not a ping
            last_message = message
            break

    # - Return if all messages are non-text (stickers or something)

    if not last_message:
        return

    # -- Check if ping needed

    is_ping_needed = _is_ping_needed(last_message) or is_unread

    if not is_ping_needed:
        return

    logger.info(f"Pinging needed", pinged_times=len(last_pings))

    # - Get sticker documents

    sticker_documents = await telegram_client.get_sticker_documents(
        mini_app_config.ping_sticker_set, mini_app_config.ping_sticker_document_ids
    )

    # - Ping if needed

    for ping_time in range(len(mini_app_config.ping_periods)):
        # - Skip if already pinged this time

        if ping_time < len(last_pings):
            logger.info(f"Already pinged this time: {ping_time}", ping_time=ping_time)
            continue

        # - Ping if enough time has passed

        if datetime.utcnow() > last_message.date.replace(tzinfo=None) + to_timedelta(
            mini_app_config.ping_periods[ping_time]
        ):
            logger.info('Ping!', ping_time=ping_time, now=datetime.utcnow(), message_date=last_message.date.replace(tzinfo=None), ping_period=to_timedelta(mini_app_config.ping_periods[ping_time]))  # fmt: skip

            # - Send sticker

            await telegram_client.send_file(dialog.input_entity, random.choice(sticker_documents))


async def groom():
    # - Get dialogs

    dialogs = await telegram_client.get_dialogs(archived=False)

    # - Select user and group chats

    dialogs = [dialog for dialog in dialogs if telegram_client.get_entity_type(dialog.entity) in ["user", "group"]]

    # - Filter old dialogs

    dialogs = [
        dialog
        for dialog in dialogs
        if dialog.message
        if datetime.utcnow()
        - to_timedelta(mini_app_config.ping_periods[-1])
        - to_timedelta(mini_app_config.dialogs_period)
        <= dialog.message.date.replace(tzinfo=None)
    ]

    # - Iterate over chats

    for dialog in dialogs:
        await ping_if_needed(dialog)


async def main(schedule_period=timedelta(days=1)):
    # - Init

    logger.info("Started grommer")

    await telegram_client.start(phone=config.telegram_phone)

    # - Cache dialogs

    async for dialog in telegram_client.iter_dialogs():
        pass

    # - Start grooming loop

    while True:
        try:
            await groom()
        except:
            logger.exception("Failed to groom")

        await asyncio.sleep(schedule_period.total_seconds())


if __name__ == "__main__":
    asyncio.run(main())
