from second_sun.deps.deps import Deps
from second_sun.deps.init_deps import init_deps

from lessmore.utils.execute_system_command import execute_system_command


def set_global_brightness(brightness: int, deps: Deps):
    # - Get all light bulbs, their ips and tokens (using miiocli cloud, but with python)

    # -- Get all devices from mi cloud as raw string

    output = execute_system_command(
        f"miiocli cloud --username {deps.config.mi_cloud_username} --password {deps.config.mi_cloud_password}"
    )

    """
== Xiaomi Smart Air Purifier 4 Pro (Device offline ) ==
	Model: zhimi.airp.vb4
	Token: acd6a69eb1024a452b6cfb49046bcb3b
	IP: 192.168.100.204 (mac: 7C:C2:94:2F:B1:7B)
	DID: 495937845
	Locale: de
== Mi Smart LED Bulb (Device online ) ==
	Model: yeelink.light.mono6
	Token: 091bd0270b499dd72ddb0c842e5da1fe
	IP: 192.168.100.162 (mac: 7C:C2:94:58:B0:23)
	DID: 506808437
	Locale: ru
== Mi Smart LED Bulb Essential (White and Color) (Device online ) ==
	Model: yeelink.light.color5
	Token: bc83f5ac3473732e9afc512957f835ff
	IP: 192.168.100.164 (mac: 7C:C2:94:81:62:5A)
	DID: 509475500
	Locale: ru
...
"""
    print(output)
    # -- Parse devices and their properties

    lines = output.split("\n")
    starting_line_indices = [i for i, line in enumerate(lines) if "==" in line]
    device_infos = [
        "\n".join(lines[starting_line_indices[i] : starting_line_indices[i + 1]])
        for i in range(len(starting_line_indices) - 1)
    ]
    print(device_infos)


def test():
    set_global_brightness(brightness=10, deps=init_deps())


if __name__ == "__main__":
    test()
