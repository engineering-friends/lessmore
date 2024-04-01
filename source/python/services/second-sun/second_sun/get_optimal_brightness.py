from datetime import datetime, timedelta

from second_sun.interpolate_on_time import interpolate_on_time


def get_optimal_brightness(
    target_time: str,
    wake_time: str = "08:00",
    sleep_time: str = "00:00",
    dawn_time: str = "06:00",
    sunrise_time: str = "06:30",
    sunset_time: str = "19:00",
    dusk_time: str = "19:30",
) -> int:
    """Get optimal brightness for given time (0-100).

    - Target brightness:
        - Waking up: 0 to 100 from waking up to 30 minutes after waking up
        - Day: 100 till 2 hours before sleep time
        - Going to sleep: 100 to 0 from 2 hours before sleep time to sleep time
        - Sleep: 0 from sleep time to wake time
    - Sun is modeled:
        - Rising: 0 to 100 from dawn to sunrise
        - Risen: 100 till sunset
        - Setting: 100 to 0 from sunset to dusk
        - Set: 0 from dusk to dawn

    The result is sun brightness with added artificial light with the best effort: ` artificial_brightness = max(0, target_brightness - sun_brightness)`
    """

    # - Get target brightness

    target_brightness = interpolate_on_time(
        time_and_values=[
            [wake_time, 0],
            [
                (
                    datetime.combine(datetime.now().date(), datetime.strptime(wake_time, "%H:%M").time())
                    + timedelta(minutes=30)
                ).strftime("%H:%M"),
                100,
            ],
            [
                (
                    datetime.combine(datetime.now().date(), datetime.strptime(sleep_time, "%H:%M").time())
                    - timedelta(hours=2)
                ).strftime("%H:%M"),
                100,
            ],
            [sleep_time, 0],
        ],
        target_time=target_time,
    )

    # - Get sun brightness

    sun_brightness = interpolate_on_time(
        time_and_values=[
            [dawn_time, 0],
            [sunrise_time, 100],
            [sunset_time, 100],
            [dusk_time, 0],
        ],
        target_time=target_time,
    )

    # - Return optimal brightness

    return round(max(0.0, target_brightness - sun_brightness))


def test():
    # - Plot brightness from 00:00 to 23:59

    import matplotlib.pyplot as plt
    import pandas as pd

    times_at = pd.date_range(start="2022-01-01", end="2022-01-02", freq="1min")
    brightness = [get_optimal_brightness(target_time=at.strftime("%H:%M")) for at in times_at]
    df = pd.DataFrame({"time": times_at, "brightness": brightness})
    df.plot(x="time", y="brightness")
    plt.show()


if __name__ == "__main__":
    test()
