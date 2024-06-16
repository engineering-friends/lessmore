# About 

A simple smart hope app to set home light automatically based on the times of dawn/sunrise/sunset/dusk, wake and sleep time.

Only yeelight bulbs are supported at the moment.

Works only on local network.

# Logic 

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
