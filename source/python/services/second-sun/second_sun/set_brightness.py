import time

from loguru import logger
from second_sun.deps.deps import Deps
from second_sun.deps.init_deps import init_deps

from lessmore.utils.execute_system_command import execute_system_command


def set_brightness(brightness: int, device: dict) -> None:
    # - Power on the bulb

    if brightness > 0:
        # - Turn on the bulb

        output = execute_system_command(
            f"miiocli yeelight --ip {device['IP'].split(" ")[0]} --token {device['Token']} on"
        )
        logger.info("Turned on the bulb", output=output)

        # - Set brightness

        output = execute_system_command(
            f"miiocli yeelight --ip {device['IP'].split(" ")[0]} --token {device['Token']} set_brightness {brightness}"
        )
        logger.info("Set brightness", output=output)

    else:
        # - Set brightness to 1

        output = execute_system_command(
            f"miiocli yeelight --ip {device['IP'].split(" ")[0]} --token {device['Token']} set_brightness 1"
        )
        logger.info("Set brightness to 1", output=output)

        # - Turn off the bulb

        output = execute_system_command(
            f"miiocli yeelight --ip {device['IP'].split(" ")[0]} --token {device['Token']} off"
        )
        logger.info("Turned off the bulb", output=output)


def test():
    # set_brightness(
    #     brightness=0,
    #     device={
    #         "title": "Mi Smart LED Bulb (Device online )",
    #         "Model": "yeelink.light.mono6",
    #         "Token": "091bd0270b499dd72ddb0c842e5da1fe", # pragma: allowlist secret
    #         "IP": "192.168.100.162 (mac: 7C:C2:94:58:B0:23)",
    #         "DID": "506808437",
    #         "Locale": "ru",
    #     },
    # )
    device = {
        "title": "Mi Smart LED Bulb (Device online )",
        "Model": "yeelink.light.mono6",
        "Token": "091bd0270b499dd72ddb0c842e5da1fe",  # pragma: allowlist secret
        "IP": "192.168.100.162 (mac: 7C:C2:94:58:B0:23)",
        "DID": "506808437",
        "Locale": "ru",
    }
    print(
        execute_system_command(f"miiocli yeelight --ip {device['IP'].split(" ")[0]} --token {device['Token']} status")
    )


if __name__ == "__main__":
    test()
