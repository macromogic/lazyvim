return {
  "ojroques/nvim-osc52",
  config = function()
    local osc52 = require("osc52")

    -- 自动 yank 到系统剪贴板
    vim.api.nvim_create_autocmd("TextYankPost", {
      callback = function()
        if vim.v.event.operator == "y" and vim.v.event.regname == "" then
          osc52.copy_register('"')
        end
      end,
    })

    -- 手动触发的快捷键
    vim.keymap.set("n", "<leader>sy", function()
      osc52.copy_register('"')
    end, { desc = "Send yank to system clipboard (OSC52)" })

    vim.keymap.set("v", "<leader>sy", function()
      osc52.copy_register('"')
    end, { desc = "Send selection to system clipboard (OSC52)" })
  end,
}
