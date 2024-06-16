import time

from datetime import datetime

from astral import LocationInfo
from astral.sun import sun
from loguru import logger
from second_sun.get_optimal_brightness import get_optimal_brightness
from second_sun.set_brightness_for_all_bulbs import set_brightness_for_all_bulbs


if __name__ == "__main__":
    while True:
        try:
            # - Get sun info

            sun = sun(
                observer=LocationInfo(
                    name="Tbilisi",
                    region="Georgia",
                    timezone="Asia/Tbilisi",
                    latitude=41.688793028637676,
                    longitude=44.69141558756124,
                ).observer,
                date=datetime.now().date(),
            )  # {"dawn": datetime.datetime(2022, 3, 15, 4, 59, 57, 116000, tzinfo=datetime.timezone(datetime.timedelta(seconds=14400), 'GET')}, ...

            # - Set brightness for all bulbs

            set_brightness_for_all_bulbs(
                brightness=get_optimal_brightness(
                    target_time=datetime.now().strftime("%H:%M"),
                    wake_time="08:00",
                    sleep_time="00:00",
                    dawn_time=sun["dawn"].strftime("%H:%M"),
                    sunrise_time=sun["sunrise"].strftime("%H:%M"),
                    sunset_time=sun["sunset"].strftime("%H:%M"),
                    dusk_time=sun["dusk"].strftime("%H:%M"),
                ),
            )
        except Exception as e:
            logger.error("Error setting brightness for all bulbs", error=e)
        time.sleep(60)
