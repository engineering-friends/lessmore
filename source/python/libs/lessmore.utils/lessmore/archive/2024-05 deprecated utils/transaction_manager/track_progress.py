import time

from datetime import datetime, timedelta

from loguru import logger

from lessmore.utils.to_anything import to_timedelta


def start_tracking_progress(transaction_manager, total=None, period="60s"):
    started_at = datetime.now()

    while True:
        values_map = transaction_manager.get_all()

        count_map = {k: len(v) for k, v in values_map.items()}

        if total:
            count_map["left"] = total - sum(count_map.values())

        logger.info("Stats", **count_map)

        if total:
            logger.info("Percents", **{k: v / total for k, v in count_map.items()})

        time.sleep(unified_timedelta.to_seconds(period))
