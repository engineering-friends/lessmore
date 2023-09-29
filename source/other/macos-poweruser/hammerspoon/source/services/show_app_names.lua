local module = {}


function applicationWatcher(appName, eventType, app)
  if (eventType == hs.application.watcher.activated) then
    if (appName ~= nil) then
      hs.alert.show("App name: " .. appName)
    end
  end
end

module.appWatcher = hs.application.watcher.new(applicationWatcher)
module.appWatcher:start()

return module
