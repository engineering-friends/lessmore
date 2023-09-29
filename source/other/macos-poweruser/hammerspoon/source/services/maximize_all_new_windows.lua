local module = {}
local tables = require("libs.tables")
local log = require("libs.log")
local time = require("libs.time")

lastMaximized = {}
lastCleanup = time.getCurrentTimestamp()
lastHeartbeat = time.getCurrentTimestamp()

hs.window.animationDuration = 0

function maximizeIfNeeded()
  -- clean lastMaximized
  if (time.getCurrentTimestamp() - lastCleanup) > 3600 then
    log.log('Last maximized clean up')
    for k, v in pairs(lastMaximized) do
      if v == nil then
        ::continue::
      end
      if (time.getCurrentTimestamp() - v) > 12 * 3600 then
        lastMaximized[k] = nil
      end
    end

    lastCleanup = time.getCurrentTimestamp()
  end

  if (time.getCurrentTimestamp() - lastHeartbeat) > 30 then
    lastHeartbeat = time.getCurrentTimestamp()
    log.logTable(lastMaximized)
  end

  window  = hs.window.frontmostWindow()
  if window == nil then
    log.log("Nil window")
    return
  end
  windowId = window:id()

  if window:isMaximizable() then
    if tables.hasKey(lastMaximized, windowId) then
      -- already maximized
      return
    end
    window:maximize() -- 0.2 - default timing for system
    lastMaximized[windowId] = time.getCurrentTimestamp()
  end
end

-- close app when last window is closed (not working on freshly opened app-window sometimes)
function cleanCache(window, appName, eventName)
    if window == nil then
      return
    end
    if tables.hasKey(lastMaximized, window:id()) then
      lastMaximized[window:id()] = nil
    end
end

module.allwindows = hs.window.filter.new(nil)
module.allwindows:subscribe(hs.window.filter.windowDestroyed, cleanCache)

module.maximizeTimer = hs.timer.new(0.1, maximizeIfNeeded)
module.maximizeTimer:start()

return module
