from telegram_poweruser.imports.runtime import *  # isort: skip

from tqdm.asyncio import tqdm as tqdm_asyncio


async def main(entities):
    # - Init client

    telegram_client = TelegramClient(
        session=os.path.join(get_root_directory(__file__), "data/dynamic/telegram_sessions/message_exporter.session"),
        api_id=config.telegram_api_id,
        api_hash=config.telegram_api_hash,
    )

    await telegram_client.start()

    # - Workaround to find channel entities by title (earlier it worked just by giving a string)

    input_dialogs = []
    for entity in entities:
        async for dialog in telegram_client.iter_dialogs():
            if dialog.title == entity:
                input_dialogs.append(dialog)
                break

    found_titles = [dialog.name for dialog in input_dialogs]
    assert len(found_titles) == len(entities), "Failed to find: {}".format(set(entities) - set(found_titles))
    entities = input_dialogs

    # - Export all the messages from now till the beginning of time

    for entity in entities:
        values = []
        async for message in tqdm_asyncio(telegram_client.iter_messages(entity, limit=None)):
            values.append([message.id, message.date, getattr(message.from_id, "user_id", None), message.raw_text])

            if to_datetime(message.date) < to_datetime("2023-02-01 00:00:00"):
                break

            time.sleep(0.01)

        df = pd.DataFrame(values, columns=["id", "date", "from_id", "text"])
        df.to_csv(f"data/dynamic/{entity.name}.csv", index=False)


asyncio.run(
    main(
        entities=[
            "TinyBetNotifier",
            "Preflop Abusers",
            "ColluderKiller_AoF",
            "ColluderKiller_allPatterns",
        ]
    )
)
