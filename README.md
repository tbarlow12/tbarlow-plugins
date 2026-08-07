# tbarlow-plugins

Personal Claude Code plugin marketplace by [Tanner Barlow](https://github.com/tbarlow12).

## Plugins

| Plugin | Description |
|--------|-------------|
| [iterm-fleet](iterm-fleet/) | Scaffold multi-agent iTerm2 workspaces |

## Installing a plugin

```bash
claude plugins install tbarlow12/tbarlow-plugins/<plugin-name>
```

## Structure

Each plugin follows the [rootstock plugin format](https://github.com/cedar-team/rootstock) (the Claude Code plugin marketplace spec):

```
<plugin-name>/
  .claude-plugin/
    plugin.json       # metadata
  bin/                # deterministic shell/python scripts
  skills/             # Claude skill definitions (SKILL.md)
  README.md
```
