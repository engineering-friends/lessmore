"""Listen to massage updates in channeled sharing topics and sync them with people. """
from telegram_poweruser.mini_apps.channeled_sharing.imports.runtime import *  # isort: skip

from telegram_poweruser.mini_apps.channeled_sharing.source.helpers import format_message_text
from telegram_poweruser.mini_apps.channeled_sharing.source.notion_topics_syncer import wait_for_topics_dataframe


# - Bot integration


async def get_target_names(topic_peer):
    # - Get penultimate topic message

    recent_messages = await telegram_client.get_messages(topic_peer, limit=2)

    if recent_messages:
        penultimate_message = recent_messages[-1]
        penultimate_message_at = to_datetime(penultimate_message.date)
    else:
        penultimate_message = None
        penultimate_message_at = to_datetime("1970.01.01")

    # - Get pre-selected target names. If present and recent - pre-select previous people. Otherwise - pre-select randomly

    if (
        penultimate_message
        and datetime.utcnow() - penultimate_message_at <= to_timedelta("6h")
        and (penultimate_message.chat_id, penultimate_message.id)
        in telegram_client.message_cache  # check that message has been processed and cached
    ):
        # - Set source of pre-selected target names (will be used later)

        pre_selected_source = "last_topic_message"

        # - Iterate over people and check if we sent them the message

        target_names = []

        for i, row in shared_memory["topics_df"][shared_memory["topics_df"]["topic_peer"] == topic_peer].iterrows():
            # - Get peer chat

            output_chat = row["target_telegram"]

            # - Get message

            message = await telegram_client.search_message(
                output_chat,
                message_key=format_message_text(
                    telegram_client.message_cache[(penultimate_message.chat_id, penultimate_message.id)],
                    row["target_called_name"],
                ),
            )

            # - Add if present

            if not message:
                logger.info("Failed to find message by text", chat=output_chat, key=telegram_client.message_cache[(penultimate_message.chat_id, penultimate_message.id)])  # fmt: skip
                continue
            else:
                target_names.append(row["target_name"])

    else:
        # - Set source of pre-selected target names (will be used later)

        pre_selected_source = "random"

        # - Get random peers by probability

        target_names = [
            row["target_name"]
            for i, row in shared_memory["topics_df"][shared_memory["topics_df"]["topic_peer"] == topic_peer].iterrows()
            if np.random.choice([0, 1], p=[1 - row["p"], row["p"]]) == 1
        ]

    # - Get updated list of target names from bot integration

    target_names = await _get_target_names_from_bot(
        pre_selected_source=pre_selected_source,
        names=[
            row["target_name"]
            for i, row in shared_memory["topics_df"][shared_memory["topics_df"]["topic_peer"] == topic_peer].iterrows()
        ],
        pre_selected_names=target_names,
    )

    return target_names


async def _get_target_names_from_bot(pre_selected_source, names, pre_selected_names):
    async with shared_memory_lock:
        # - Set shared memory for bot

        shared_memory["names_selector"]["names"] = names
        shared_memory["names_selector"]["pre_selected_names"] = pre_selected_names
        shared_memory["names_selector"]["pre_selected_source"] = pre_selected_source

        # - Start telegram bot for choosing names

        await telegram_client.send_message(config.telegram_bot_name, "/start")

        # - Wait for telegram bot to handle names

        while "selected_names" not in shared_memory["names_selector"]:
            await asyncio.sleep(0.1)

        # - Take names

        target_names = shared_memory["names_selector"]["selected_names"]

        # - Clear shared memory

        shared_memory["names_selector"] = {}

    return target_names


# - Callbacks


@telegram_client.on(events.NewMessage(outgoing=True))
async def on_new_message(event):
    logger.info("on_new_message", event=event)

    # - Preprocess arguments

    input_message = event

    # - Wait for topics to be initialized

    await wait_for_topics_dataframe()

    # - Cast peer

    peer = await telegram_client.cast_peer(event.input_chat)

    # - Return if chat is not a topic chat

    if peer not in shared_memory["topics_df"]["topic_peer"].tolist():
        logger.info("Chat is not a topic chat", peer=peer)
        return

    # - Process photos

    if isinstance(input_message.media, MessageMediaPhoto):
        # - Album is being processed at the moment, wait a little bit

        # todo maybe: create more clean solution [@marklidenberg]
        await asyncio.sleep(2)

        # - Check if album is being processed

        if shared_memory.get("is_album_processing"):
            logger.info("Album photo, skipping")
            return

    # - Save message key to message_cache

    telegram_client.message_cache[(input_message.chat_id, input_message.id)] = telegram_client.get_message_key(
        input_message
    )

    # - Get target names

    target_names = await get_target_names(topic_peer=peer)

    # - Send message to target_names

    for i, row in shared_memory["topics_df"][shared_memory["topics_df"]["topic_peer"] == peer].iterrows():
        # - Skip non-target rows

        if row["target_name"] not in target_names:
            continue

        # - Unfold row

        topic, output_chat, p = row["topic"], row["target_telegram"], row["p"]

        # - Send message

        if input_message.fwd_from:
            # - Forward

            await telegram_client.forward_messages(output_chat, input_message.message)
        else:
            # - Format

            formatted_text = format_message_text(input_message.text, row["target_called_name"])

            # - Send

            if input_message.media:
                if isinstance(input_message.media, MessageMediaWebPage):
                    # input_message.photo may be true
                    logger.info("Sending new message", topic=topic, chat=output_chat, text=formatted_text)
                    await telegram_client.send_message(output_chat, formatted_text)
                elif isinstance(input_message.media, MessageMediaPhoto):
                    logger.info("Sending photo", topic=topic, chat=output_chat, text=formatted_text)
                    await telegram_client.send_file(output_chat, input_message.media, caption=formatted_text)
                elif isinstance(input_message.media, MessageMediaDocument):
                    logger.info("Sending file", topic=topic, chat=output_chat, text=formatted_text)
                    await telegram_client.send_file(
                        output_chat, input_message.media, caption=formatted_text, force_document=True
                    )
                else:
                    logger.error(f"Unknown media type: {type(input_message.media)}")
            else:
                logger.info("Sending new message", topic=topic, chat=output_chat, text=formatted_text)
                await telegram_client.send_message(output_chat, formatted_text)

    logger.debug("Current cache", cache=dict(telegram_client.message_cache))


@telegram_client.on(events.Album())
async def on_new_album(event):
    logger.info("on_new_album", event=event)

    # - Set album_processing flag (when album arrives, photo messages also arrive separately. We skip those in on_new_message by this flag and process only album, without duplicating messages)

    shared_memory["is_album_processing"] = True

    # - Global try-except to clear is_album_processing flag

    try:
        # - Wait for topics from notion

        await wait_for_topics_dataframe()

        # - Cast peer

        peer = await telegram_client.cast_peer(event.input_chat)

        # - Return if peer is not a topic peer

        if peer not in shared_memory["topics_df"]["topic_peer"].tolist():
            return

        # - Get target names

        target_names = await get_target_names(peer)

        # - Send target names

        for i, row in shared_memory["topics_df"][shared_memory["topics_df"]["topic_peer"] == peer].iterrows():
            # - Return if row is not in target_names

            if row["target_name"] not in target_names:
                continue

            # - Get output chat

            output_chat = row["target_telegram"]

            logger.info("Sending album", chat=output_chat)

            # - Format

            formatted_text = format_message_text(event.text, row["target_called_name"])

            # - Save message key to message_cache

            for message in event.messages:
                telegram_client.message_cache[(message.chat_id, message.id)] = telegram_client.get_message_key(message)

            # - Send album files

            await telegram_client.send_file(
                output_chat, [message.media for message in event.messages], caption=formatted_text
            )
        shared_memory["is_album_processing"] = False
    except:
        shared_memory["is_album_processing"] = False
        raise


@telegram_client.on(events.MessageDeleted())
async def on_message_deleted(event):
    logger.debug("on_message_deleted", event=event)

    # - Wait for topics from notion

    await wait_for_topics_dataframe()

    # - Process empty input chat

    if not event.input_chat:
        # NOTE: I do not know why this one happens
        return

    # - Cast peer

    peer = await telegram_client.cast_peer(event.input_chat)

    # - Return if peer is not a topic peer

    if peer not in shared_memory["topics_df"]["topic_peer"].tolist():
        return

    # - Process deleted_ids

    for message_id in event.deleted_ids:
        # - Return if message is not cached (we get ids only, but not text. But look for the message by text - which is stored in cache)

        if (event.chat_id, message_id) not in telegram_client.message_cache:
            logger.info("Did not find message in cache", chat_id=event.chat_id, message_id=message_id)
            continue

        # - Iterate over people

        for i, row in shared_memory["topics_df"][shared_memory["topics_df"]["topic_peer"] == peer].iterrows():
            # - Get output chat

            output_chat = row["target_telegram"]

            # - Get deleting message

            message = await telegram_client.search_message(
                output_chat,
                message_key=format_message_text(
                    telegram_client.message_cache[(event.chat_id, message_id)], row["target_called_name"]
                ),
            )

            # - Return if message not found

            if not message:
                logger.info("Failed to find message by text", chat=output_chat, key=telegram_client.message_cache[(event.chat_id, message_id)])  # fmt: skip
                continue

            # - Delete message from person

            logger.info("Deleting message", chat=output_chat, message_id=message.id)
            await telegram_client.delete_messages(output_chat, message.id)

        # - Pop deleted message from cache

        telegram_client.message_cache.pop((event.chat_id, message_id))

    logger.debug("Current cache", cache=dict(telegram_client.message_cache))


@telegram_client.on(events.MessageEdited())
async def on_message_edited(event):
    logger.info("on_message_edited", event=event)

    # - Wait for notion topics

    await wait_for_topics_dataframe()

    # - Cast peer

    peer = await telegram_client.cast_peer(event.input_chat)

    # - Return if peer is not a topic peer

    if peer not in shared_memory["topics_df"]["topic_peer"].tolist():
        return

    # - Set input message

    input_message = event

    # - Return if message not cached

    if (input_message.chat_id, input_message.id) not in telegram_client.message_cache:
        logger.info("Did not find message in cache", chat_id=input_message.chat_id, message_id=input_message.id)
        return

    # - Iterate over people

    for i, row in shared_memory["topics_df"][shared_memory["topics_df"]["topic_peer"] == peer].iterrows():
        # - Get output chat

        output_chat = row["target_telegram"]

        # - Get message

        message = await telegram_client.search_message(
            output_chat,
            message_key=format_message_text(
                telegram_client.message_cache[(input_message.chat_id, input_message.id)], row["target_called_name"]
            ),
        )

        # - Return if message not found

        if not message:
            logger.info("Failed to find message by text", chat=output_chat, key=telegram_client.message_cache[(input_message.chat_id, input_message.id)])  # fmt: skip
            continue

        # - Edit message

        logger.info("Editing message", chat=output_chat, message_id=message.id)
        await telegram_client.edit_message(
            output_chat, message.id, format_message_text(input_message.text, row["target_called_name"])
        )

    # - Clear cache

    telegram_client.message_cache[(input_message.chat_id, input_message.id)] = telegram_client.get_message_key(
        input_message
    )

    logger.debug("Current cache", cache=dict(telegram_client.message_cache))
