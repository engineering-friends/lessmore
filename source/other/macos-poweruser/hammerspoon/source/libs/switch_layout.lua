local module = {}

local log = require('libs.log')

all_layouts = hs.keycodes.layouts()
module.switchLayout = function()
  log.log('Switching layout...')
  local cur_layout = hs.keycodes.currentLayout()
  if cur_layout == all_layouts[#all_layouts] then
    hs.keycodes.setLayout(all_layouts[1])
  else
    for k, v in pairs(all_layouts) do
      if cur_layout == v then
        hs.keycodes.setLayout(all_layouts[k + 1])
      end
    end
  end
    log.log('Switching layout done!')
end

return module
