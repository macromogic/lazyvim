return {
  {
    "m4xshen/hardtime.nvim",
    dependencies = { "MunifTanjim/nui.nvim" },
    -- 软启动，不立刻 block，只提示
    opts = {
      enabled = true,                -- 插件默认启用
      restriction_mode = "hint",      -- 使用提示 (hint) 模式，而不是完全阻止 (block)

      -- 限制重复按键的配置
      max_time = 800,                 -- ms：如果在这个时间内重复按键，会被算作重复
      max_count = 3,                  -- 重复按键次数上限

      -- 哪些键属于 “restricted keys” 会被提示
      restricted_keys = {
        -- 举例：方向键、 hjkl、w/b/e 等看你觉得自己用得多的
        ["<Up>"] = { "n", "i" },
        ["<Down>"] = { "n", "i" },
        ["<Left>"] = { "n", "i" },
        ["<Right>"] = { "n", "i" },
        ["h"] = { "n" },
        ["l"] = { "n" },
        ["j"] = { "n" },
        ["k"] = { "n" },
        -- 还可以加 word motion 重复的键
        ["w"] = { "n" },
        ["b"] = { "n" },
        ["e"] = { "n" },
      },

      -- 哪些键是被直接禁用（disabled） — 小心用，先留空或者只极少用
      disabled_keys = {
        -- 比如不禁用箭头，只做提示，用空表
        ["<Up>"] = {},
        ["<Down>"] = {},
      },

      -- 哪些文件类型不启用这个插件 / 不提示
      disabled_filetypes = {
        "help",
        "nvim-tree",
        "dashboard",
        "lazy",
        "mason",
        "Trouble",
        "qf",
        -- 可以根据你常用的插件或类型加
      },

      hint = true,                    -- 提示功能开
      notification = true,            -- 弹通知（或者 command line 写提示）
      timeout = 2000,                 -- 通知显示时间
    },

    -- 可选：自己定义一个 keymap /命令来手动启用 /禁用，方便你控制
    config = function(_, opts)
      require("hardtime").setup(opts)

      -- 比如 +leader+h 启用 / +leader+H 禁用
      vim.keymap.set("n", "<leader>h", ":Hardtime toggle<CR>", { desc = "Toggle Hardtime hint mode" })
      vim.keymap.set("n", "<leader>r", ":Hardtime report<CR>", { desc = "Show Hardtime report" })
    end,
  },
}
