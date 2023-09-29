local module = {}

local switchLayout = require("libs.switch_layout")
local sendKey = require("libs.send_key")
local hotkeyUtils = require("libs.hotkey_utils")
local log = require('libs.log')

-- map hotkeys
-- todo maybe: move to keyword arguments with a table hack: https://www.lua.org/pil/5.3.html
hotkeyUtils.mapHotkey("Global", {"ctrl"}, "§", {"fn", "cmd"}, "down")
hotkeyUtils.mapHotkey("Global", {"ctrl"}, "tab", {"fn", "cmd"}, "up")
hotkeyUtils.mapHandler("Global", {"cmd"}, "f10", function() sendKey.sendSystemKey("MUTE") end)
hotkeyUtils.mapHandler("Global", {"cmd"}, "f11", function() sendKey.sendSystemKey("SOUND_DOWN") end, true)
hotkeyUtils.mapHandler("Global", {"cmd"}, "forwarddelete", function() sendKey.sendSystemKey("SOUND_UP") end, true)
hotkeyUtils.mapHandler("Global", {}, "f17", switchLayout.switchLayout) -- Hyper key when pressed once

hotkeyUtils.mapHotkey("Notion", {"cmd"}, "t", {"cmd", "shift"}, "n")

hotkeyUtils.mapHotkey("Google Chrome", {"option"}, "tab", {"cmd", "ctrl", "shift", "option"}, "2")
hotkeyUtils.mapHotkey("Google Chrome", {"option", "shift"}, "tab", {"cmd", "ctrl", "shift", "option"}, "1")
hotkeyUtils.mapHotkey("Google Chrome", {"cmd"}, "p", {"cmd", "shift"}, ".")   -- https://github.com/Fannon/search-bookmarks-history-and-tabs#readme

-- jupyter notebook, black auto save
local function applyBlackAndSave()
	-- cmd + shift +b
    sendKey.sendKeyEvent("ctrl", true)
    sendKey.sendKeyEvent("b", true)
    sendKey.sendKeyEvent("b", false)
    sendKey.sendKeyEvent("ctrl", false)

	-- cmd + s
    sendKey.sendKeyEvent("cmd", true)
    sendKey.sendKeyEvent("s", true)
    sendKey.sendKeyEvent("s", false)
    sendKey.sendKeyEvent("cmd", false)
end
hotkeyUtils.mapHandler("Google Chrome", {"cmd"}, "b", applyBlackAndSave)   -- https://github.com/Fannon/search-bookmarks-history-and-tabs#readme


hotkeyUtils.mapHotkey("Safari", {"option"}, "tab", {"cmd", "ctrl", "shift", "option"}, "n")
hotkeyUtils.mapHotkey("Safari", {"option", "shift"}, "tab", {"cmd", "ctrl", "shift", "option"}, "p")

hotkeyUtils.mapHotkey("Finder", {"cmd"}, "l", {"cmd", "shift"}, "g")
hotkeyUtils.mapHotkey("Finder", {}, "forwarddelete", {"cmd"}, "delete")

hotkeyUtils.mapHotkey("Slack", {"cmd"}, "p", {"cmd"}, "k")

hotkeyUtils.mapHotkey("Telegram", {"cmd"}, "p", {"cmd"}, "f")

hotkeyUtils.mapHotkey("iTerm2", {"cmd"}, "p", {"ctrl"}, "r")

hotkeyUtils.mapHotkey("PyCharm", {"cmd"}, ";", {"cmd"}, "'", false, 2)


for context, hotkeys in pairs(hotkey_dic) do
	log.log("Configuring " .. context)
	if context == "Global" then
		hotkeyUtils.configureGlobalHotkeys()
	end
end

module.hotkeysAppWatcher = hs.application.watcher.new(update)
module.hotkeysAppWatcher:start()

return module
