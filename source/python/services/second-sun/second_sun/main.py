import time

from datetime import datetime

from loguru import logger
from second_sun.deps.init_deps import init_deps
from second_sun.get_optimal_brightness import get_optimal_brightness
from second_sun.set_brightness_for_all_bulbs import set_brightness_for_all_bulbs


if __name__ == "__main__":
    deps = init_deps()
    while True:
        try:
            set_brightness_for_all_bulbs(
                brightness=get_optimal_brightness(
                    target_time=datetime.now().strftime("%H:%M"),
                    wake_time="08:00",
                    sleep_time="00:00",
                    dawn_time="06:00",
                    sunrise_time="06:30",
                    sunset_time="19:00",
                    dusk_time="19:30",
                ),
                deps=deps,
            )
        except Exception as e:
            logger.error("Error setting brightness for all bulbs", error=e)
        time.sleep(60)
