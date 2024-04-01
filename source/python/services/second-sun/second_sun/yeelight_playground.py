from yeelight import Bulb

from lessmore.utils.easy_printing.print_json import print_json


bulb = Bulb("192.168.100.162")
bulb.turn_on()
# bulb.turn_off()
bulb.set_brightness(1, duration=500)
