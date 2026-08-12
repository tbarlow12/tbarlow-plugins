# iterm-fleet

Scaffold multi-agent iTerm2 workspaces. Clone repos into numbered agent directories and generate a tiled iTerm2 arrangement so each pane runs an independent agent instance with its own git working tree.

## Why

Running multiple AI agents in parallel requires isolated repo clones — agents writing to the same working tree stomp on each other's git state. iterm-fleet automates the scaffolding: `N` clones per repo, one pane per clone, all wired up as a saved iTerm2 arrangement.

## Usage

Once installed, run the `fleet` skill:

```
/fleet
```

The skill walks you through setup interactively.

## What it sets up

Given 3 repos and 6 agents:

```
~/repos/
  1/api/      2/api/      3/api/      4/api/      5/api/      6/api/
  1/frontend/ 2/frontend/ 3/frontend/ 4/frontend/ 5/frontend/ 6/frontend/
  1/infra/    2/infra/    3/infra/    4/infra/    5/infra/    6/infra/
```

iTerm2 arrangement: one tab per repo, 3×2 grid of panes (agents 1–6).

## Config

`~/.config/iterm-fleet/fleet.yaml`:

```yaml
base_dir: ~/repos
agent_count: 6
cols: 3
rows: 2
screen:
  width: 1920
  height: 1056
iterm2:
  profile: Default
  arrangement_path: ~/Library/Application Support/iTerm2/Arrangements/fleet.iterm2arrangement
  badge_color: gray            # optional — name or 'r,g,b'; default gray; applied to both the iTerm2 profile's light- and dark-mode badge color, so it renders correctly regardless of the app's current appearance
  badge_width_fraction: 0.25   # optional — global iTerm2 badge size pref
  badge_height_fraction: 0.15  # optional
tab_colors:                    # optional — cycles if fewer colors than repos
  - red
  - blue
repos:
  - git@github.com:org/repo-one.git
  - git@github.com:org/repo-two.git
```

`fleet-init`'s repo prompt uses `gh` (if installed and authenticated) to list
every repo you have access to, sorted by most recently updated, and lets you
multi-select with `fzf` (if installed) or a paginated numbered menu. Falls
back to pasting URLs manually if `gh` isn't set up.

## Iterating on a running fleet

Once a fleet is set up, these edit `fleet.yaml` and (for most) rebuild +
reopen the arrangement automatically:

| Command | What it does |
|---|---|
| `fleet-status` | Print the current config at a glance |
| `fleet-apply` | Rebuild + reopen (what most of the commands below do for you already) |
| `fleet-add-repo <url>` | Add a repo (then `fleet-clone` + `fleet-apply`) |
| `fleet-remove-repo <name>` | Remove a repo |
| `fleet-set-font <size> [family]` | Change the linked iTerm2 profile's font |
| `fleet-set-tab-colors <color...>` | Set the per-repo tab color palette |
| `fleet-set-badge <color> [w-frac] [h-frac]` | Set badge color and/or size |
| `fleet-set-layout <colsxrows>` | Change the pane grid (e.g. `3x2`) |
| `fleet-set-agent-count <n>` | Change agent count (then `fleet-clone` + `fleet-apply`) |
| `fleet-set-arrangement-path <path>` | Change where the `.iterm2arrangement` file is written |

Named colors: `red blue green amber orange teal purple olive gray cyan pink
yellow white`, or raw `'r,g,b'` floats between 0 and 1.

## Requirements

- macOS with iTerm2 installed
- Python 3 (stdlib only — no pip installs)
- git
- `gh` (optional) — enables the repo picker in `fleet-init`; falls back to manual URL paste without it
- `fzf` (optional) — real checkbox multi-select for the repo picker; falls back to a numbered menu without it
