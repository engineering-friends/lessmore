from telegram_poweruser.imports.runtime import *  # isort: skip

# - Notion

notion_client = NotionClient(auth=config.notion_token)

# - Shared Memory

shared_memory = {
    "topics_df": pd.DataFrame(columns=["topic", "topic_peer", "target_telegram", "target_called_name", "p"]),
    "names_selector": {},  # {'pre_selected_names': [...], 'names': [...], 'selected_names': [...]}  # api_callback will put pre_selected_names + names in shared memory on new message. Bot will process current message and put selected_names here. api_callback will take selected_names and clear SHARED_MEMORY
}
shared_memory_lock = asyncio.Lock()

# - Telegram

telegram_client = TelegramClient(
    session=os.path.join(get_root_directory(__file__), "data/dynamic/telegram_sessions/channeled_sharing.session"),
    api_id=config.telegram_api_id,
    api_hash=config.telegram_api_hash,
)
