return {
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        clangd = {
          cmd = {
            "clangd",
            "--background-index",
            "--completion-style=detailed",
            "--header-insertion=iwyu",
            "--query-driver=**",
            "--compile-commands-dir=build"
          },
          filetypes = { "c", "cpp", "cuda" },
        },
      },
    },
  },
}
