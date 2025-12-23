return {
  {
    "simrat39/rust-tools.nvim",
    config = function()
      require("rust-tools").setup {}

      local function is_rust_project()
        return vim.fn.findfile("Cargo.toml", vim.loop.cwd()) ~= ""
      end

      local function bind_rust_tools_keys()
        vim.keymap.set("n", "<leader>cr", "<cmd>RustRun<CR>", { desc = "Rust Run" })
        vim.keymap.set("n", "<leader>cd", "<cmd>RustDebuggables<CR>", { desc = "Rust Debuggables" })
        vim.keymap.set("n", "<leader>cC", "<cmd>RustOpenCargo<CR>", { desc = "Open Cargo.toml" })
        vim.keymap.set("n", "<leader>ct", "<cmd>RustTest<CR>", { desc = "Rust Test" })
        vim.keymap.set("n", "<leader>cb", "<cmd>Cargo build<CR>", { desc = "Rust Build" })
      end

      if is_rust_project() then
        bind_rust_tools_keys()
      end

      vim.api.nvim_create_autocmd("BufRead", {
        pattern = "Cargo.toml",
        callback = bind_rust_tools_keys,
      })

      vim.api.nvim_create_autocmd("DirChanged", {
        pattern = "*",
        callback = function()
          if is_rust_project() then
            bind_rust_tools_keys()
          end
        end,
      })
    end,
  }
}