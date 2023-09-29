local module = {}


module.sendSystemKey = function (key)
    hs.eventtap.event.newSystemKeyEvent(key, true):post()
    hs.eventtap.event.newSystemKeyEvent(key, false):post()
    hs.timer.usleep(100 * 1000)
end

module.sendKey = function (key)
    hs.eventtap.event.newKeyEvent(key, true):post()
    hs.eventtap.event.newKeyEvent(key, false):post()
    hs.timer.usleep(100 * 1000)
end

module.sendKeyEvent = function (key, action)
    hs.eventtap.event.newKeyEvent(key, action):post()
    hs.timer.usleep(25 * 1000)
end
module.sendSystemKeyEvent = function (key, action)
    hs.eventtap.event.newSystemKeyEvent(key, action):post()
    hs.timer.usleep(25 * 1000)
end

return module