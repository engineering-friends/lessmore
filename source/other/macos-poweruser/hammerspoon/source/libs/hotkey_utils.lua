local module = {}
local log = require("libs.log")
local tables = require("libs.tables")
local utils = require('libs.utils')


-- App-specific hotkey
function rebindedHotkey(modifiers_from, letter_from, handler, should_repeat)
  if should_repeat then
    repeat_handler = handler
  else
    repeat_handler = nil
  end
  return hs.hotkey.new(modifiers_from, letter_from, handler, nil, repeat_handler)
end

EN_KEYMAP = {["2"]=19, ["1"]=18, ["0"]=29, ["/"]=44, ["\\."]=47, ["\\-"]=27, [","]=43, ["shift"]=56, ["9"]=25, ["8"]=28, ["7"]=26, ["6"]=22, ["5"]=23, ["4"]=21, ["3"]=20, ["capslock"]=57, ["ctrl"]=59, ["f14"]=107, ["f8"]=100, ["f18"]=79, ["f4"]=118, ["space"]=49, ["f19"]=80, ["pad2"]=84, ["pad7"]=89, ["f11"]=103, ["\'"]=39, ["pad3"]=85, ["down"]=125, ["§"]=10, ["f16"]=106, ["alt"]=58, ["padclear"]=71, ["up"]=126, ["pad9"]=92, ["kana"]=104, ["f7"]=98, ["underscore"]=94, ["f3"]=99, ["f17"]=64, ["left"]=123, ["escape"]=53, [":"]=24, ["delete"]=51, [";"]=41, ["padenter"]=76, ["pad\\."]=65, ["pageup"]=116, ["f1"]=122, ["f15"]=113, ["pad="]=81, ["home"]=115, ["f13"]=105, ["r"]=15, ["q"]=12, ["p"]=35, ["o"]=31, ["n"]=45, ["m"]=46, ["l"]=37, ["k"]=40, ["z"]=6, ["y"]=16, ["x"]=7, ["w"]=13, ["v"]=9, ["f2"]=120, ["t"]=17, ["s"]=1, ["b"]=11, ["a"]=0, ["`"]=50, ["help"]=114, ["pad"]=75, ["\\]"]=30, ["\\\\"]=42, ["rightcmd"]=54, ["j"]=38, ["i"]=34, ["h"]=4, ["g"]=5, ["f"]=3, ["e"]=14, ["d"]=2, ["c"]=8, ["f12"]=111, ["f10"]=109, ["\x10"]=104, ["forwarddelete"]=117, ["f20"]=90, ["pad8"]=91, ["end"]=119, ["eisu"]=102, ["pad\\*"]=67, ["fn"]=63, ["rightctrl"]=62, ["pad6"]=88, ["pad\\-"]=78, ["tab"]=48, ["return"]=36, ["pad0"]=82, ["pad1"]=83, ["yen"]=93, ["pad4"]=86, ["f6"]=97, ["\\["]=33, ["rightshift"]=60, ["u"]=32, ["pad,"]=95, ["pad\\+"]=69, ["right"]=124, ["f9"]=101, ["rightalt"]=61, ["cmd"]=55, ["pad5"]=87, ["pagedown"]=121, ["f5"]=96}

function getKeyCode(key)
  return EN_KEYMAP[key] or key
end



function strokeHandler(modifiers_to, letter_to, times)
    -- Fill functions to stroke in a sequence
    local functionSequence = {}

    if not times then
        times = 1
    end

    for i = 1, times do
        table.insert(functionSequence, hs.fnutils.partial(hs.eventtap.keyStroke, modifiers_to, getKeyCode(letter_to)))
        if times ~= 1 then
            table.insert(functionSequence, hs.fnutils.partial(hs.timer.usleep, 100 * 1000))
        end
    end
    return utils.sequenceRunner(table.unpack(functionSequence))

end

hotkey_dic = {}
module.mapHandler = function(context, modifiers_from, letter_from, handler, should_repeat)
    -- Init empty table
	if hotkey_dic[context] == nil then
		hotkey_dic[context] = {}
	end
	hotkey = rebindedHotkey(modifiers_from, letter_from, handler, should_repeat)
	table.insert(hotkey_dic[context], hotkey)
end

module.mapHotkey = function(context, modifiers_from, letter_from, modifiers_to, letter_to, should_repeat, times)
	module.mapHandler(context, modifiers_from, getKeyCode(letter_from), strokeHandler(modifiers_to, letter_to, times), should_repeat)
end


function enableHotkeys(context)
  if not tables.hasKey(hotkey_dic, context) then
    return
  end
  log.log('Enable ' .. context)
  for k, v in pairs(hotkey_dic[context]) do
    v:enable()
  end
end

function disableHotkeys(context)
  if not tables.hasKey(hotkey_dic, context) then
    return
  end
 log.log('Disable ' .. context)
  for k, v in pairs(hotkey_dic[context]) do
    v:disable()
  end
end

local WF = hs.window.filter

function update(appName, eventType, app)
  if appName == nil then
    return
  end
  if (eventType == hs.application.watcher.activated) then
    enableHotkeys(appName)
  elseif (eventType == hs.application.watcher.deactivated) then
    disableHotkeys(appName)
  end
end

module.configureGlobalHotkeys = function()
	enableHotkeys("Global")
end

return module
