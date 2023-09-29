local module = {}

module.hasValue = function(table, val)
    for index, value in ipairs(table) do
        if value == val then
            return true
        end
    end
    return false
end

module.hasKey = function(table, key)
    for k, v in pairs(table) do
        if k == key and v ~= nil then
            return true
        end
    end

    return false
end

module.filter = function(table, filterIter)
  local out = {}

  for k, v in pairs(t) do
    if filterIter(k, v, table) then out[k] = v end
  end

  return out
end

return module
