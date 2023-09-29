local module = {}


module.sequenceRunner = function(...)
  local arg = table.pack(...)
  return function()
    local results = {}
    for _, fn in ipairs(arg) do
        local result = fn()
        if result then
            table.insert(results, result)
        end
    end
    return results
  end
end

return module
