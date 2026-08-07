---
name: fleet
model: sonnet
description: |
  Set up a multi-agent iTerm2 workspace. Clones repos into numbered agent directories
  and generates a tiled arrangement so each pane runs an independent agent instance.
  Use when setting up a new machine, adding repos to an existing fleet, or rebuilding
  the iTerm2 arrangement after a config change.
  Keywords: fleet, iterm2, arrangement, workspace, multi-agent, setup, clone repos, agents
compatibility: Requires Python 3, git, and iTerm2 installed on macOS. `gh` and `fzf` are optional (enable the repo picker in fleet-init).
allowed-tools: Bash(fleet-init *) Bash(fleet-clone *) Bash(fleet-build *) Bash(fleet-open *) Bash(fleet-apply *) Bash(fleet-status *) Bash(fleet-add-repo *) Bash(fleet-remove-repo *) Bash(fleet-set-font *) Bash(fleet-set-badge *) Bash(fleet-set-tab-colors *) Bash(fleet-set-layout *) Bash(fleet-set-agent-count *) Bash(fleet-set-arrangement-path *) Bash(ls *) Bash(cat *) Bash(find *) Read AskUserQuestion
---

# fleet

Sets up a multi-agent iTerm2 workspace: each repo is cloned into `{base}/{1..N}/`
so agents can work in parallel without stomping on each other's git state. An iTerm2
arrangement is generated with one tab per repo, one pane per agent.

## Locate plugin bin directory

The plugin's installed location varies (marketplace cache path, dev checkout,
etc.) — don't hardcode a guess. Find it once per session:

```bash
find ~/.claude/plugins -maxdepth 6 -type d -path '*iterm-fleet/*/bin' 2>/dev/null
```

```bash
PLUGIN_BIN="<the path that command found>"
ls "$PLUGIN_BIN"
```

Expected: `fleet-init`, `fleet-clone`, `fleet-build`, `fleet-open`, `fleet-apply`,
`fleet-status`, `fleet-add-repo`, `fleet-remove-repo`, `fleet-set-font`,
`fleet-set-badge`, `fleet-set-tab-colors`, `fleet-set-layout`,
`fleet-set-agent-count`, `fleet-set-arrangement-path`, plus internal `_fleet_*.py`
helper modules (not directly invoked).

## Step 1: Check for existing config

```bash
ls ~/.config/iterm-fleet/fleet.yaml 2>/dev/null && echo "exists" || echo "missing"
```

- **exists** → show the user the current config (`cat ~/.config/iterm-fleet/fleet.yaml`) and ask if they want to change it or just rebuild
- **missing** → run `fleet-init`

## Step 2: Run fleet-init (if needed)

```bash
"$PLUGIN_BIN/fleet-init"
```

This is interactive — let the user answer the prompts. Do not pre-fill answers.
When it finishes, confirm the written config looks correct before continuing.

The repo-selection prompt tries `gh` first (if installed and authenticated):
it lists every repo the user has access to, sorted by most recently updated,
and lets them multi-select via `fzf` (real checkbox UI) if installed, or a
paginated numbered menu otherwise. It falls back to manual URL paste if `gh`
isn't set up or nothing gets picked — that's expected, not an error.

## Step 3: Clone repos

```bash
"$PLUGIN_BIN/fleet-clone"
```

This clones each repo into `{base_dir}/{1..N}/{repo-name}/`. If a clone already
exists it does a `git pull --ff-only` instead. Watch for errors — a failed clone
should be reported and the user asked how to proceed before continuing.

## Step 4: Build the arrangement

```bash
"$PLUGIN_BIN/fleet-build"
```

Generates the `.iterm2arrangement` file. If it fails, read the error carefully:
- **fleet.yaml not found** → re-run Step 2
- **Permission denied** → check output directory permissions
- **Other** → show the full error to the user

## Step 5: Open in iTerm2

```bash
"$PLUGIN_BIN/fleet-open"
```

This imports the arrangement into iTerm2. If iTerm2 is not running it will be
launched first. Tell the user to use **Window → Restore Arrangement → fleet**
if the window doesn't appear automatically.

## Iterating on a running fleet

Once a fleet exists, prefer the dedicated tool over hand-editing fleet.yaml
or re-running fleet-init — each one updates the config and (except where
noted) rebuilds + reopens automatically:

- `fleet-status` — show current config before making a change
- `fleet-add-repo <url>` — then run `fleet-clone` and `fleet-apply` (does NOT auto-apply: new agent dirs need cloning first)
- `fleet-remove-repo <name>` — auto-applies
- `fleet-set-font <size> [family]` — auto-applies. Changes the *iTerm2 profile itself* (global, not scoped to fleet panes)
- `fleet-set-tab-colors <color...>` — auto-applies. Named colors: `red blue green amber orange teal purple olive gray cyan pink yellow white`, or `'r,g,b'` floats
- `fleet-set-badge <color> [width-frac] [height-frac]` — auto-applies. The fraction args are a *global* iTerm2 preference (`BadgeMaxWidthFraction`/`BadgeMaxHeightFraction`), not per-arrangement — mention this to the user before changing it
- `fleet-set-layout <colsxrows>` — auto-applies. Pane count comes from cols×rows, not agent_count — warns if they don't match
- `fleet-set-agent-count <n>` — then run `fleet-clone` and `fleet-apply` (does NOT auto-apply, same reason as add-repo)
- `fleet-set-arrangement-path <path>` — auto-applies. Warns if the path doesn't end in `.iterm2arrangement` (see Edge cases below for why that extension matters)

If the user just changed fleet.yaml by hand (rare — the tools above are
preferred), `fleet-apply` alone is equivalent to fleet-build + fleet-open.

## Edge cases

- **Repo already cloned but dirty**: `fleet-clone` does `git pull --ff-only` and will
  fail if there are local changes. Tell the user to stash or commit first in that
  agent directory.
- **Agent count changed**: new clones will be created for the new agent numbers;
  existing ones are untouched.
- **iTerm2 not installed**: `fleet-open` will fail. Tell the user to install iTerm2
  from iterm2.com.
- **Arrangement already open in iTerm2**: iTerm2 may warn about replacing the current
  arrangement — tell the user to confirm the replacement.
- **Arrangement file extension**: must be `.iterm2arrangement` (what iTerm2's
  `Info.plist` actually registers), not `.itermArrangement` — the latter has no
  app association and silently fails to open. `fleet-set-arrangement-path` warns
  if you set the wrong one.
- **Font renders tiny**: panes need a real, matching iTerm2 profile font linked
  in (via `Normal Font` in the arrangement's Bookmark) — an unlinked bookmark
  with no font set falls back to a tiny default, independent of Columns/Rows.
  Don't try to fix this by pointing the Bookmark's `Guid` at the real profile's
  own Guid — that makes iTerm treat the session as "launch this saved profile
  fresh," discarding the per-session Working Directory and Tab Color overrides.
  Use `fleet-set-font` rather than hand-editing this.
