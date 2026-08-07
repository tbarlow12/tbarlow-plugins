---
name: fleet
model: sonnet
description: |
  Set up a multi-agent iTerm2 workspace. Clones repos into numbered agent directories
  and generates a tiled arrangement so each pane runs an independent agent instance.
  Use when setting up a new machine, adding repos to an existing fleet, or rebuilding
  the iTerm2 arrangement after a config change.
  Keywords: fleet, iterm2, arrangement, workspace, multi-agent, setup, clone repos, agents
compatibility: Requires Python 3, git, and iTerm2 installed on macOS.
allowed-tools: Bash(fleet-init *) Bash(fleet-clone *) Bash(fleet-build *) Bash(fleet-open *) Bash(ls *) Bash(cat *) Read AskUserQuestion
---

# fleet

Sets up a multi-agent iTerm2 workspace: each repo is cloned into `{base}/{1..N}/`
so agents can work in parallel without stomping on each other's git state. An iTerm2
arrangement is generated with one tab per repo, one pane per agent.

## Locate plugin bin directory

```bash
PLUGIN_BIN="$HOME/.rootstock/plugins/iterm-fleet/bin"
```

Confirm the scripts are present:

```bash
ls "$PLUGIN_BIN"
```

Expected: `fleet-init`, `fleet-clone`, `fleet-build`, `fleet-open`.

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

## Rebuilding after config changes

If the user only changed the fleet.yaml (added a repo, changed agent count):
- Re-run Steps 3 and 4 only (clone + build). No need to re-run fleet-init.
- Re-run Step 5 to load the new arrangement.

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
