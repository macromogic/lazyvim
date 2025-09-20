return {
  -- 1) Copilot 主插件
  {
    "zbirenbaum/copilot.lua",
    cmd = "Copilot",
    build = ":Copilot auth", -- 第一次安装后执行一次登录
    opts = {
      suggestion = { enabled = false }, -- 用 blink.cmp 集成，就关掉内置 ghost text
      panel = { enabled = false },
      filetypes = {
        markdown = true,
        help = false,
        ["*"] = true, -- 其他文件类型默认开启
      },
    },
  },

  -- 2) 把 Copilot 接到 blink.cmp
  {
    "saghen/blink.cmp",
    optional = true,
    dependencies = {
      "giuxtaposition/blink-cmp-copilot",
    },
    opts = {
      sources = {
        default = { "copilot" },
        providers = {
          copilot = {
            name = "copilot",
            module = "blink-cmp-copilot",
            score_offset = 100,
            async = true,
          },
        },
      },
    },
  },

  -- 3) 可选：调整补全源的优先级，让 Copilot 更靠前
  --[[
  {
    "saghen/blink.cmp",
    opts = function(_, opts)
      opts.sources = opts.sources or {}
      local has = false
      for _, s in ipairs(opts.sources) do
        if s.name == "copilot" then
          has = true
          s.priority = 200 -- 比 lsp/snippets 更高即可
        end
      end
      if not has then
        table.insert(opts.sources, 1, { name = "copilot", priority = 200 })
      end

      return opts
    end,
  },
  --]]
}
