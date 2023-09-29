local module = {}

module.helloWorld = function()
  hs.alert.show("Hello World!")
end

-- hello-World
hs.hotkey.bind({"cmd", "option"}, "A", function()
  module.helloWorld()
end)

-- move window
hs.hotkey.bind({"cmd", "option"}, "B", function()
  local win = hs.window.focusedWindow()
  local f = win:frame()

  f.x = f.x - 10
  win:setFrame(f)
end)

-- tile to left border
hs.hotkey.bind({"cmd", "option"}, "C", function()
  local win = hs.window.focusedWindow()
  local f = win:frame()
  local screen = win:screen()
  local max = screen:frame()

  f.x = max.x
  f.y = max.y
  f.w = max.w / 2
  f.h = max.h
  win:setFrame(f)
end)

-- Show hello world when opening finder
-- allwindows = hs.window.filter.new(nil) -- subscribe to all windows
windowFilter = hs.window.filter.new(false):setAppFilter('Finder')
windowFilter:subscribe(hs.window.filter.windowFocused, module.helloWorld)

-- Get title of current app
hs.hotkey.bind({"cmd", "option"}, "E", function()
  app = hs.application.frontmostApplication()
  hs.alert.show(app:title())
end)

-- Run in app
hs.hotkey.bind({"cmd", "option"}, "O", function()
  app = hs.application.frontmostApplication()
  if app:title() == "Finder" then
  	log.log("Inside Finder")
  else
  	log.log("Outside Finder")
  end
end)


return module
