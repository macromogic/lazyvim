#!/usr/bin/env python3
"""Advance lazy-lock.json with a minimum release age.

Runs `Lazy! update` to fetch every plugin, then pins each one to the newest
commit on its branch that is at least --min-age-days old, never moving a
plugin backwards. `Lazy! restore` checks those commits out, the lock must
come back unchanged, and a plain headless start must not raise errors.
Run from the config's root, with nvim using this checkout as its config.
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

LOCK = Path("lazy-lock.json")
ERRORS = ("Error detected while processing", "E5108:", "E5113:")


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

    picked, moves = {}, []
    for name, entry in fetched.items():
        repo, branch = plugins / name, entry["branch"]
        prev = old.get(name, {}).get("commit")
        # Where the branch stood at the cutoff: its first-parent history, so
        # an old commit merged in only recently doesn't count as old.
        cand = git(repo, "rev-list", "-1", "--first-parent", f"--before={cutoff}",
                   f"origin/{branch}")
        if not cand:
            # Every commit is too new: keep the old pin, or for a plugin new
            # to the lock, the one lazy installed.
            commit = prev or entry["commit"]
        elif prev and git(repo, "merge-base", "--is-ancestor", cand, prev,
                          check=False) == 0:
            commit = prev
        else:
            commit = cand
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

    rc, out = nvim()
    if rc != 0 or any(e in out for e in ERRORS):
        sys.exit(f"Headless start failed after the update:\n{out}")

    print("\n".join(moves) or "Nothing to update.")
    if opts.summary and moves:
        opts.summary.write_text("\n".join(moves) + "\n")


if __name__ == "__main__":
    main()
