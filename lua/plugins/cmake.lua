return {
  {
    "Civitasv/cmake-tools.nvim",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "mfussenegger/nvim-dap",
    },
    config = function()
      require("cmake-tools").setup {
        cmake_command = "cmake",
        cmake_build_directory = "build",
        cmake_generate_options = { "-DCMAKE_EXPORT_COMPILE_COMMANDS=1" },
        cmake_regenerate_on_save = true,
        cmake_build_type = "Debug",
      }

      -- 绑定 CMake 快捷键
      local function bind_cmake_keys()
        vim.keymap.set("n", "<leader>cg", "<cmd>CMakeGenerate<CR>", { desc = "CMake Generate" })
        vim.keymap.set("n", "<leader>cb", "<cmd>CMakeBuild<CR>", { desc = "CMake Build" })
        vim.keymap.set("n", "<leader>cR", "<cmd>CMakeRun<CR>", { desc = "CMake Run" })
        vim.keymap.set("n", "<leader>cc", "<cmd>CMakeClean<CR>", { desc = "CMake Clean" })
        vim.keymap.set("n", "<leader>ct", "<cmd>CMakeSelectBuildType<CR>", { desc = "CMake Select Build Type" })
        vim.keymap.set("n", "<leader>co", "<cmd>CMakeOpen<CR>", { desc = "Open CMake Console" })
      end

      -- 判断是否是 CMake 项目（根目录有 CMakeLists.txt）
      local function is_cmake_project()
        return vim.fn.findfile("CMakeLists.txt", ".;") ~= ""  -- 在当前目录及父目录查找 CMakeLists.txt
      end

      -- 判断并绑定快捷键
      if is_cmake_project() then
        bind_cmake_keys()
      end

      -- 监听 CMakeLists.txt 文件打开时，绑定快捷键
      vim.api.nvim_create_autocmd("BufRead", {
        pattern = "CMakeLists.txt",  -- 只监听打开 CMakeLists.txt 文件
        callback = bind_cmake_keys,  -- 绑定快捷键
      })

      -- 监听目录变化时，判断是否是 CMake 项目并绑定快捷键
      vim.api.nvim_create_autocmd("DirChanged", {
        pattern = "*",
        callback = function()
          if is_cmake_project() then
            bind_cmake_keys()
          end
        end,
      })
    end,
  },
}
