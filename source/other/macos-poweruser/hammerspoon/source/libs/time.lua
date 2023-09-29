local module = {}


module.getCurrentTimestamp = function ()
  return os.time(os.date("!*t"))
end


return module

