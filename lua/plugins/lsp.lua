return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        clangd = {
          mason = false,
          cmd = {
            vim.fn.expand("~/.nix-profile/bin/clangd"),
            "--background-index",
            "--completion-style=detailed",
            "--header-insertion=iwyu",
          },
          filetypes = { "c", "cpp", "cuda" },
        },
        pyright = {
          settings = {
            python = {
              analysis = {
                typeCheckingMode = "basic",
                autoImportCompletions = true,
              },
            },
          },
        },
        rust_analyzer = {
          settings = {
            ["rust-analyzer"] = {
              cargo = {
                allFeatures = true,
              },
              procMacro = {
                enable = true,
              },
            },
          },
        },
      },
    },
  },
}
