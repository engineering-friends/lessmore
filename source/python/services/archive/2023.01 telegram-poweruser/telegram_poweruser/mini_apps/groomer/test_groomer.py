from telegram_poweruser.imports.runtime import *  # isort: skip

from telegram_poweruser.mini_apps.groomer.groomer import PING_PERIODS


def test():
    global PING_PERIODS
    PING_PERIODS.clear()
    PING_PERIODS += [timedelta(seconds=5), timedelta(days=10)]
    print(PING_PERIODS)


if __name__ == "__main__":
    test()
