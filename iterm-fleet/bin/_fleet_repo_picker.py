#!/usr/bin/env python3
"""
Interactive repo picker for fleet-init, backed by `gh`.

Fetches every repo the authenticated gh user has access to (owned + org +
collaborator), sorted by most recently updated, and lets the user pick a
subset — via `fzf --multi` (real checkbox UI) if installed, or a paginated
numbered list otherwise.

Prints one clone URL per line to stdout. Prints nothing and exits non-zero
if `gh` isn't available/authenticated, so callers can fall back to manual
URL entry.

Not meant to be run standalone for scripting — it's interactive (reads from
the real terminal, not stdin, so it still works when invoked via $(...)
command substitution in fleet-init).
"""
import json
import shutil
import subprocess
import sys

PAGE_SIZE = 20


def fetch_repos():
    proc = subprocess.run(
        ['gh', 'api', '--paginate', 'user/repos?sort=updated&direction=desc&per_page=100'],
        capture_output=True, text=True, timeout=30,
    )
    if proc.returncode != 0:
        return None
    items = []
    decoder = json.JSONDecoder()
    raw = proc.stdout
    idx = 0
    while idx < len(raw):
        chunk = raw[idx:].lstrip()
        if not chunk:
            break
        obj, end = decoder.raw_decode(chunk)
        items.extend(obj if isinstance(obj, list) else [obj])
        idx += (len(raw[idx:]) - len(chunk)) + end
    return items


def pick_with_fzf(repos):
    lines = [f"{r['full_name']}\t{'private' if r['private'] else 'public'}\t{r['updated_at'][:10]}"
             for r in repos]
    proc = subprocess.run(
        ['fzf', '--multi', '--delimiter=\t', '--with-nth=1,2,3',
         '--header=TAB to select, ENTER to confirm, ESC to cancel — repos by most recently updated'],
        input='\n'.join(lines), capture_output=True, text=True,
    )
    if proc.returncode not in (0, 1):  # 1 = no selection made, not an error
        return None
    selected_names = {line.split('\t')[0] for line in proc.stdout.splitlines() if line}
    return [r for r in repos if r['full_name'] in selected_names]


def parse_selection(s, n):
    """Parse '1,3,5-8' style input into a set of 0-based indices within [0, n)."""
    picked = set()
    for part in s.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            a, b = part.split('-', 1)
            try:
                a, b = int(a), int(b)
            except ValueError:
                continue
            for i in range(min(a, b), max(a, b) + 1):
                if 1 <= i <= n:
                    picked.add(i - 1)
        else:
            try:
                i = int(part)
            except ValueError:
                continue
            if 1 <= i <= n:
                picked.add(i - 1)
    return picked


def pick_with_menu(repos):
    try:
        tty = open('/dev/tty')
    except OSError:
        return []
    picked_indices = set()
    page = 0
    total = len(repos)
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    while True:
        start = page * PAGE_SIZE
        chunk = repos[start:start + PAGE_SIZE]
        print(f"\n-- page {page + 1}/{pages} ({total} repos, most recently updated first) --",
              file=sys.stderr)
        for i, r in enumerate(chunk, start=1):
            mark = '*' if (start + i - 1) in picked_indices else ' '
            vis = 'private' if r['private'] else 'public '
            print(f"  [{mark}] {start + i:3d}  {r['full_name']:<45} {vis}  {r['updated_at'][:10]}",
                  file=sys.stderr)
        print("Enter numbers/ranges to toggle (e.g. 1,3,5-8), "
              "'n'/'p' for next/prev page, 'done' to finish, 'q' to cancel:", file=sys.stderr)
        print("> ", end='', file=sys.stderr, flush=True)
        line = tty.readline().strip()
        if line in ('done', ''):
            break
        if line == 'q':
            return []
        if line == 'n':
            page = min(page + 1, pages - 1)
            continue
        if line == 'p':
            page = max(page - 1, 0)
            continue
        for i in parse_selection(line, total):
            if i in picked_indices:
                picked_indices.discard(i)
            else:
                picked_indices.add(i)
    return [repos[i] for i in sorted(picked_indices)]


def main():
    if not shutil.which('gh'):
        sys.exit(1)
    auth = subprocess.run(['gh', 'auth', 'status'], capture_output=True, timeout=10)
    if auth.returncode != 0:
        sys.exit(1)

    repos = fetch_repos()
    if not repos:
        sys.exit(1)

    if shutil.which('fzf'):
        selected = pick_with_fzf(repos)
    else:
        selected = pick_with_menu(repos)

    if not selected:
        sys.exit(1)

    for r in selected:
        print(r['clone_url'])


if __name__ == '__main__':
    main()
