import time

from loguru import logger
from second_sun.custom_yeelight_bulb import CustomYeelightBulb
from yeelight import discover_bulbs


def set_brightness_for_all_bulbs(brightness: int) -> None:
    # - Get bulbs

    bulbs = discover_bulbs()
    # [
    #  {
    #   "ip": "192.168.100.162",
    #   "port": 55443,
    #   "capabilities": {
    #    "id": "0x000000001e354875",
    #    "model": "mono6",
    #    "fw_ver": "14",
    #    "support": "get_prop set_default set_power toggle set_ct_abx set_bright start_cf stop_cf set_scene cron_add cron_get cron_del set_adjust adjust_bright adjust_ct set_name",
    #    "power": "on",
    #    "bright": "100",
    #    "color_mode": "2",
    #    "ct": "3900",
    #    "rgb": "0",
    #    "hue": "0",
    #    "sat": "0",
    #    "name": ""
    #   }
    #  }
    #
    # ]

    logger.info("Got bulbs", bulbs=bulbs)

    # - Set brightness
    for bulb in bulbs:
        logger.info(f"Setting brightness for bulb", ip=bulb["ip"], brightness=brightness)
        CustomYeelightBulb(ip=bulb["ip"]).set_brightness_smoothly(brightness=brightness, duration=2)


def test():
    for i in range(100):
        set_brightness_for_all_bulbs(brightness=i)
        time.sleep(1)


if __name__ == "__main__":
    test()
