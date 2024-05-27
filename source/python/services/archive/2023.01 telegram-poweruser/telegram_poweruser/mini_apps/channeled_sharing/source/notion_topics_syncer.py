"""Load dataframe of topics from notion. Sync channels with topics. """

from telegram_poweruser.mini_apps.channeled_sharing.imports.runtime import *  # isort: skip

# - Notion updater


async def get_topics_df():
    logger.info("Getting topics dataframe...")  # todo later: return format [@marklidenberg]

    # - Get topic dataframes in different runtime modes

    if config.runtime_mode == "test":
        # - Return pre-saved topics dataframe

        rows = pd.read_csv(os.path.join(get_root_directory(__file__), "data/static/test_topics_df.csv")).values.tolist()
    else:
        # - Download topics dataframe from notion

        # -- Get pages

        topic_pages = notion_client.query_database_pages(mini_app_config.topics_database_id)

        # -- Iterate over pages and collect topic dataframe values

        rows = []

        for topic_page in topic_pages:
            row = []  # todo later: example [@marklidenberg]
            row.append(mini_app_config.channel_name_prefix + topic_page.title)

            for channel_page in notion_client.get_page_property(topic_page, mini_app_config.channels_property_name):
                # - Add name

                row.append(notion_client.get_page_property(channel_page, mini_app_config.name_property_name))

                # - Add telegram

                telegram = notion_client.get_page_property(channel_page, mini_app_config.telegram_property_name)
                if not telegram:
                    logger.exception("No telegram property found", channel_page_title=channel_page.title)
                    continue
                else:
                    row.append(telegram)

                # - Add called_name

                called_name = notion_client.get_page_property(channel_page, mini_app_config.called_name_property_name)
                if not called_name:
                    logger.exception("No called name property found", channel_page_title=channel_page.title)
                    continue
                else:
                    row.append(called_name)

                # - Add channeled sharing probability

                row.append(topic_page["properties"][mini_app_config.probability_property_name]["number"] or 0)

                # - Add peer as None for now (will be filled later)

                row.append(None)

                # - Add row

                rows.append(row)

    df = pd.DataFrame(
        rows, columns=["topic", "target_name", "target_telegram", "target_called_name", "p", "topic_peer"]
    )

    # - Add metatopic to all

    if config.central_channel_name:
        # - Add central channel to all topics

        central_channel_rows = []
        for topic in df["topic"].unique():
            central_channel_rows.append(
                [topic, "Channeled Sharing Central", mini_app_config.central_channel_name, "Друг", 1, None]
            )

        # - Update dataframe

        df = pd.DataFrame(
            rows + central_channel_rows,
            columns=["topic", "target_name", "target_telegram", "target_called_name", "p", "topic_peer"],
        )

    # - Sort by probability (desc) and target name

    df["_minus_p"] = -df["p"]
    df = df.sort_values(by=["_minus_p", "target_name"])
    df.pop("_minus_p")

    # - Sync channels

    if config.runtime_mode != "test":
        # - Collect current topics from channels

        current_topics = []
        for dialog in await telegram_client.get_dialogs(archived=False):
            if dialog.title.startswith(mini_app_config.channel_name_prefix):
                current_topics.append(dialog.title)

        # - Set new topics

        new_topics = set(df["topic"].unique())

        # - Process delta

        if set(current_topics) != set(new_topics):
            # - Delete unused

            logger.info("Unused channels found, deleting...")
            for topic in set(current_topics) - set(new_topics):
                await telegram_client.delete_channel(topic)

            # - Create new and add to topics folder

            # -- Create new channels

            new_chat_ids = []
            for topic in set(new_topics) - set(current_topics):
                result = await telegram_client.create_channel(topic)
                chat_id = result.chats[0].id
                new_chat_ids.append(chat_id)

            # -- Wait for channels to initialize (otherwise sometimes they are not added to folders)

            await asyncio.sleep(3)  # todo maybe: optimize [@marklidenberg]

            # -- Update folder

            await telegram_client.add_chats_to_folder(new_chat_ids, mini_app_config.folder_title)

    # - Add peers to dataframe

    df["topic_peer"] = [await telegram_client.get_input_entity(row["topic"]) for i, row in df.iterrows()]
    df["topic_peer"] = [await telegram_client.cast_peer(row["topic_peer"]) for i, row in df.iterrows()]

    # - Format telegram field

    def _format(value):
        # - Process empty

        if not value:
            return ""

        # - Process url

        value = value.replace("https://t.me/", "")  # https://t.me/marklidenberg -> marklidenberg

        # - Add @ if needed

        if value[0] != "@":
            value = "@" + value
        return value

    df["target_telegram"] = df["target_telegram"].apply(_format)

    # - Return

    logger.info("Updated topics dataframe", df=df)
    return df


async def start_notion_update_loop():
    # - Cache dialogs

    async for dialog in telegram_client.iter_dialogs():
        pass

    # - Wait for telethon_client to connect properly. Otherwise, it may not work

    await asyncio.sleep(5)  # wait for telethon_client to connect properly. Otherwise, it may not work

    # - Start updater loop

    last_updated_at = None
    editing_session_opened = False

    while True:
        try:
            # - Get last edited time

            last_edited_at = notion_client.get_database_last_edit_time(mini_app_config.topics_database_id)

            if not last_updated_at:
                logger.info("Initializing notion topics")

                # - Set last updated

                last_updated_at = last_edited_at

                # - Update topics df

                shared_memory["topics_df"] = await get_topics_df()

                continue

            elif not editing_session_opened:
                logger.info("Editing session is closed")

                # - Open session if needed

                if last_edited_at != last_updated_at:
                    logger.info(
                        "Opening editing session",
                        last_edited_at=last_edited_at,
                        last_updated_at=last_updated_at,
                    )
                    editing_session_opened = True
                else:
                    # - Sleep extra 10 seconds (don't remember why)

                    await asyncio.sleep(10)
                continue
            else:
                logger.info("Editing session is opened")

                if last_edited_at < datetime.utcnow().replace(tzinfo=None) - timedelta(minutes=1):
                    """Closing session"""

                    logger.info("Closing session")

                    # - Close editing session

                    # -- Set new last_updated_at

                    last_updated_at = last_edited_at

                    # -- Get current topics_df

                    shared_memory["topics_df"] = await get_topics_df()

                    # -- Set editing_session flag

                    editing_session_opened = False
                    logger.info("Closing editing session", last_edited_at=last_edited_at, last_updated_at=last_updated_at, topics_df=str(shared_memory['topics_df']))  # fmt: skip

                else:
                    logger.info("Waiting for session to close")
                    await asyncio.sleep(10)
        except:
            logger.exception("Error in notion updater")
            await asyncio.sleep(60)


async def wait_for_topics_dataframe():
    # - Return if already initialized

    if len(shared_memory["topics_df"]) >= 1:
        return

    # - Wait till initialized

    logger.info("Waiting for initialization...")

    while len(shared_memory["topics_df"]) == 0:
        await asyncio.sleep(3)

    logger.info("Successfully waited for initialization")
