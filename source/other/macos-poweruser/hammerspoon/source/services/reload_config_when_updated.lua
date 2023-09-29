-- - Load libs
local module = {}

local reload_config = require("libs.reload_config")
module.watcher = hs.pathwatcher.new(os.getenv("HOME") .. "/.hammerspoon/", reload_config.reloadConfig):start()


module.reloadTimer = hs.timer.doAfter(3600 * 24 * 7, hs.reload)

return module