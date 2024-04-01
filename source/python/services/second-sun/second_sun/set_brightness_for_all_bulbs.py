import time

from loguru import logger
from second_sun.deps.deps import Deps
from second_sun.deps.init_deps import init_deps

from lessmore.utils.execute_system_command import execute_system_command


def set_brightness_for_all_bulbs(brightness: int, deps: Deps) -> None:
    logger.info("Setting brightness for all bulbs...", brightness=brightness)

    # - Get all light bulbs, their ips and tokens (using miiocli cloud, but with python)

    # -- Get all devices from mi cloud as raw string

    logger.info("Getting bulb devices...")
    output = execute_system_command(
        f"miiocli cloud --username {deps.config.mi_cloud_username} --password {deps.config.mi_cloud_password}"
    )

    # [DEBUG]
    #     output = """
    # == Xiaomi Smart Air Purifier 4 Pro (Device offline ) ==
    # 	Model: zhimi.airp.vb4
    # 	Token: acd6a69eb1024a452b6cfb49046bcb3b
    # 	IP: 192.168.100.204 (mac: 7C:C2:94:2F:B1:7B)
    # 	DID: 495937845
    # 	Locale: de
    # == Mi Smart LED Bulb (Device online ) ==
    # 	Model: yeelink.light.mono6
    # 	Token: 091bd0270b499dd72ddb0c842e5da1fe
    # 	IP: 192.168.100.162 (mac: 7C:C2:94:58:B0:23)
    # 	DID: 506808437
    # 	Locale: ru
    #     """.strip()

    # -- Parse devices and their properties

    lines = output.split("\n")
    starting_line_indices = [i for i, line in enumerate(lines) if "==" in line]
    device_infos = [
        "\n".join(
            lines[
                starting_line_indices[i] : starting_line_indices[i + 1] if i + 1 < len(starting_line_indices) else None
            ]
        )
        for i in range(len(starting_line_indices))
    ]

    devices = []

    for device_info in device_infos:
        lines = device_info.strip().split("\n")
        devices.append(
            {
                "title": lines[0].strip("= ").strip(),
                **{line.split(": ")[0].strip(): line.split(": ", 1)[1].strip() for line in lines[1:]},
            }
        )
    """
    [  {
  "title": "Mi WiFi Range Extender AC1200 (Device offline )",
  "Model": "xiaomi.repeater.v6",
  "Token": "33415a6f4763444b7a45794b5a70304b", # pragma: allowlist secret
  "IP": "192.168.100.3 (mac: a4:39:b3:a8:d1:bd)",
  "DID": "579810583",
  "Locale": "ru"
 }, ...]
 """

    # - Set brightness for all light bulbs

    bulb_devices = [device for device in devices if "bulb" in device["title"].lower()]

    logger.info("Got bulb devices", n=len(bulb_devices), bulb_devices=bulb_devices)

    for bulb_device in [device for device in devices if "bulb" in device["title"].lower()]:
        logger.info("Setting brightness for bulb", brightness=brightness, bulb_device=bulb_device)
        try:
            execute_system_command(
                f"miiocli yeelight --ip {bulb_device['IP'].split(' ')[0]} --token {bulb_device['Token']} set_brightness {brightness}"
            )
        except Exception as e:
            logger.error("Error setting brightness for bulb", bulb_device=bulb_device, error=e)


def test():
    for i in range(100):
        set_brightness_for_all_bulbs(brightness=i, deps=init_deps())
        time.sleep(1)


if __name__ == "__main__":
    test()
