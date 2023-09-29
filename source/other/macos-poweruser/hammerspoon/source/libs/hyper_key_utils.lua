
local module = {}
local sendKey = require("libs.send_key")
local log = require("libs.log")

module.hyperMode = hs.hotkey.modal.new({}, 'F16') -- f16 is just a random non-used key

function enterHyperMode()
   module.hyperMode:enter()
end

function exitHyperMode()
   module.hyperMode:exit()
end

function strokeHandler(modifiers_to, letter_to)
  return hs.fnutils.partial(hs.eventtap.keyStroke, modifiers_to, letter_to)
end

module.mapHandler = function(modifiers_from, letter_from, handler)
   module.hyperMode:bind(modifiers_from, letter_from, handler)
end

module.mapHotkey = function(modifiers_from, letter_from, modifiers_to, letter_to)
   module.hyperMode:bind(modifiers_from, letter_from, strokeHandler(modifiers_to, letter_to))
end


-- Binds the enter/exit functions of the Hyper modal to all combinations of modifiers
module.install = function(hotKey)
  hs.hotkey.bind({}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"shift"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"ctrl"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"ctrl", "shift"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"cmd"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"cmd", "shift"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"cmd", "ctrl"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"cmd", "ctrl", "shift"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"alt"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"alt", "shift"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"alt", "ctrl"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"alt", "ctrl", "shift"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"alt", "cmd"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"alt", "cmd", "shift"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"alt", "cmd", "ctrl"}, hotKey, enterHyperMode, exitHyperMode)
  hs.hotkey.bind({"alt", "cmd", "shift", "ctrl"}, hotKey, enterHyperMode, exitHyperMode)
end

return module
