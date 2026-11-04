#!/usr/bin/env python3
"""Advance lazy-lock.json with a minimum release age.

Runs `Lazy! update` to fetch every plugin, then pins each one to the newest
eligible release or branch commit that is at least --min-age-days old.
Respects lazy.nvim version ranges, tags, commits and pins. `Lazy! restore`
checks those commits out, the lock must come back unchanged, and loading
blink.cmp must not raise errors.
Run from the config's root, with nvim using this checkout as its config.
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

LOCK = Path("lazy-lock.json")
ERRORS = ("Error detected while processing", "Error in ", "E5108:", "E5113:",
          "Failed to run `config`", "Failed to source")


def nvim(*cmds):
    args = ["nvim", "--headless"]
    for cmd in cmds:
        args += ["-c", cmd]
    args += ["-c", "qa"]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=1800)
    return proc.returncode, proc.stdout + proc.stderr


def git(repo, *args, check=True):
    proc = subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=check)
    return proc.stdout.strip() if check else proc.returncode


def read_lock():
    return json.loads(LOCK.read_text())


def write_lock(lock):
    # The layout lazy.nvim itself writes, so its rewrites leave no diff.
    lines = [f'  {json.dumps(name)}: {{ "branch": {json.dumps(e["branch"])}, '
             f'"commit": {json.dumps(e["commit"])} }}'
             for name, e in sorted(lock.items())]
    LOCK.write_text("{\n" + ",\n".join(lines) + "\n}\n")


def plugin_targets():
    # Use lazy's own semver implementation rather than interpreting ranges here.
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp) / "targets.json"
        lua = r"""
local config = require('lazy.core.config')
local git = require('lazy.manage.git')
local targets = {}
for name, plugin in pairs(config.plugins) do
  if not plugin._.is_local then
    local version = plugin.version
    if version == nil and plugin.branch == nil then
      version = config.options.defaults.version
    end
    local target = {}
    if plugin.pin or plugin.commit or plugin.tag then
      target.fixed = true
    elseif version then
      local versions = git.get_versions(plugin.dir, version)
      table.sort(versions, function(a, b) return b < a end)
      target.releases = {}
      for _, v in ipairs(versions) do
        table.insert(target.releases, v.tag)
      end
      -- Keep empty version ranges distinct from branch tracking.
      target.versioned = true
    end
    targets[name] = target
  end
end
vim.fn.writefile({vim.json.encode(targets)}, %s)
""" % json.dumps(str(dest))
        rc, out = nvim("lua " + lua)
        if rc != 0 or not dest.exists():
            sys.exit(f"Could not read lazy.nvim plugin constraints:\n{out}")
        return json.loads(dest.read_text())


def pick_commit(repo, entry, prev, target, cutoff):
    if target.get("fixed"):
        return entry["commit"]
    if target.get("versioned"):
        for tag in target["releases"]:
            commit = git(repo, "rev-parse", f"refs/tags/{tag}^{{commit}}")
            timestamp = git(repo, "for-each-ref", "--format=%(creatordate:iso-strict)",
                            f"refs/tags/{tag}")
            if dt.datetime.fromisoformat(timestamp) <= dt.datetime.fromisoformat(cutoff):
                return commit
        # Never keep an old pin outside the declared version range.
        allowed = {git(repo, "rev-parse", f"refs/tags/{tag}^{{commit}}")
                   for tag in target["releases"]}
        if prev in allowed:
            return prev
        raise ValueError(f"No release satisfies the version range and minimum age: {repo.name}")
    cand = git(repo, "rev-list", "-1", "--first-parent", f"--before={cutoff}",
               f"origin/{entry['branch']}")
    if not cand:
        if prev:
            return prev
        raise ValueError(f"No commit satisfies minimum age: {repo.name}")
    if prev and git(repo, "merge-base", "--is-ancestor", cand, prev, check=False) == 0:
        return prev
    return cand


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--min-age-days", type=int, default=7)
    ap.add_argument("--summary", type=Path,
                    help="write one line per moved plugin here")
    opts = ap.parse_args()

    data = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    plugins = data / "nvim" / "lazy"
    cutoff = (dt.datetime.now(dt.timezone.utc)
              - dt.timedelta(days=opts.min_age_days)).isoformat()

    old = read_lock()
    rc, out = nvim("Lazy! update")
    if rc != 0:
        sys.exit(f"Lazy! update failed:\n{out}")
    fetched = read_lock()
    targets = plugin_targets()

    picked, moves = {}, []
    for name, entry in fetched.items():
        repo, branch = plugins / name, entry["branch"]
        prev = old.get(name, {}).get("commit")
        commit = pick_commit(repo, entry, prev, targets[name], cutoff)
        picked[name] = {"branch": branch, "commit": commit}
        if commit != prev:
            moves.append(f"{name}: {(prev or 'new')[:7]} -> {commit[:7]}")
    moves += [f"{name}: removed" for name in sorted(old.keys() - picked.keys())]

    write_lock(picked)
    rc, out = nvim("Lazy! restore")
    got = read_lock()
    write_lock(picked)
    missed = [f"{name}: wanted {e['commit'][:7]}, got "
              f"{got.get(name, {}).get('commit', 'nothing')[:7]}"
              for name, e in picked.items() if got.get(name) != e]
    if rc != 0 or missed:
        sys.exit("Lazy! restore didn't check out the picked commits:\n"
                 + "\n".join(missed) + f"\n{out}")

    rc, out = nvim("lua require('lazy').load({plugins={'blink.cmp'}})",
                   "lua vim.wait(2000)",
                   "lua assert(require('blink.cmp').get_lsp_capabilities().textDocument.completion)")
    if rc != 0 or any(e in out for e in ERRORS):
        sys.exit(f"Headless start failed after the update:\n{out}")

    print("\n".join(moves) or "Nothing to update.")
    if opts.summary and moves:
        opts.summary.write_text("\n".join(moves) + "\n")


if __name__ == "__main__":
    main()
