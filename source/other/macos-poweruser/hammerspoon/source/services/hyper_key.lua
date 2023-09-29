local module = {}
local sendKey = require("libs.send_key")
local log = require("libs.log")
local hyperKeyUtils = require("libs.hyper_key_utils")

local function openEmojiInput()
    sendKey.sendKeyEvent("ctrl", true)
    sendKey.sendKeyEvent("cmd", true)
    sendKey.sendKeyEvent("space", true)
    sendKey.sendKeyEvent("space", false)
    sendKey.sendKeyEvent("cmd", false)
    sendKey.sendKeyEvent("ctrl", false)
end

hyperKeyUtils.install('F18') -- Hyper key when used as modifier
hyperKeyUtils.mapHandler({}, 'r', hs.reload)
hyperKeyUtils.mapHandler({}, "e", openEmojiInput)

return module
