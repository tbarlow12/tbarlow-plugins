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
  arrangement_path: ~/Library/Application Support/iTerm2/Arrangements/fleet.itermArrangement
repos:
  - git@github.com:org/repo-one.git
  - git@github.com:org/repo-two.git
```

## Requirements

- macOS with iTerm2 installed
- Python 3 (stdlib only — no pip installs)
- git
