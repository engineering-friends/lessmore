import time

from yeelight import Bulb, discover_bulbs


class CustomYeelightBulb(Bulb):
    def set_brightness_smoothly(self, brightness: int, duration: float = 2):
        """
        Parameters
        ----------
        brightness: int from 0 to 100 (0 means the device is off)
        duration: int, seconds to change brightness
        """

        if brightness == 0:
            self.set_brightness_smoothly(brightness=1, duration=duration)
            time.sleep(duration)
            self.turn_off()
        else:
            self.turn_on()
            self.set_brightness(brightness, duration=int(duration * 1000))


def test():
    # print_json(discover_bulbs())
    bulb = CustomYeelightBulb(ip="192.168.100.162")
    bulb.set_brightness_smoothly(brightness=0, duration=2)


if __name__ == "__main__":
    test()
