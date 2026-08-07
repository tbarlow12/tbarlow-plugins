"""Shared fleet.yaml load/save for iterm-fleet tools.

fleet.yaml is a small, fixed-shape config — not full YAML — parsed with
targeted regexes rather than a YAML library dependency. save() regenerates
the whole file deterministically from the config dict rather than doing
surgical text edits, so tools can't corrupt the file by editing it out of
order.
"""
import os
import re
from datetime import datetime, timezone

DEFAULT_PATH = os.path.expanduser('~/.config/iterm-fleet/fleet.yaml')
DEFAULT_ARR_PATH = '~/Library/Application Support/iTerm2/Arrangements/fleet.iterm2arrangement'


def _get(text, key):
    m = re.search(rf'^{key}:\s*(.+)$', text, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else None


def _get_nested(text, parent, child):
    m = re.search(rf'^{parent}:\s*\n(?:.*\n)*?\s+{child}:\s*(.+)$', text, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else None


def _get_list(text, key):
    items = []
    in_section = False
    for line in text.splitlines():
        if line.strip() == f'{key}:':
            in_section = True
            continue
        if in_section:
            if line.startswith(' ') or line.startswith('\t'):
                val = line.strip().lstrip('- ').strip().strip('"').strip("'")
                if val:
                    items.append(val)
            else:
                in_section = False
    return items


def load(path=None):
    path = path or DEFAULT_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"fleet.yaml not found at {path} — run fleet-init first")
    text = open(path).read()

    return {
        'path': path,
        'base_dir': os.path.expanduser(_get(text, 'base_dir') or '~/repos'),
        'agent_count': int(_get(text, 'agent_count') or 6),
        'cols': int(_get(text, 'cols') or 3),
        'rows': int(_get(text, 'rows') or 2),
        'width': float(_get_nested(text, 'screen', 'width') or 1920),
        'height': float(_get_nested(text, 'screen', 'height') or 1056),
        'profile': _get_nested(text, 'iterm2', 'profile') or 'Default',
        'arrangement_path': os.path.expanduser(
            _get_nested(text, 'iterm2', 'arrangement_path') or DEFAULT_ARR_PATH),
        'badge_color': _get_nested(text, 'iterm2', 'badge_color'),
        'badge_width_fraction': _get_nested(text, 'iterm2', 'badge_width_fraction'),
        'badge_height_fraction': _get_nested(text, 'iterm2', 'badge_height_fraction'),
        'tab_colors': _get_list(text, 'tab_colors'),
        'repos': _get_list(text, 'repos'),
    }


def save(cfg):
    path = cfg['path']
    lines = [
        '# iterm-fleet configuration',
        f'# Last updated by iterm-fleet tools on {datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}',
        '',
        f"base_dir: {cfg['base_dir']}",
        f"agent_count: {cfg['agent_count']}",
        f"cols: {cfg['cols']}",
        f"rows: {cfg['rows']}",
        'screen:',
        f"  width: {int(cfg['width'])}",
        f"  height: {int(cfg['height'])}",
        'iterm2:',
        f"  profile: {cfg['profile']}",
        f"  arrangement_path: \"{cfg['arrangement_path']}\"",
    ]
    if cfg.get('badge_color'):
        lines.append(f"  badge_color: {cfg['badge_color']}")
    if cfg.get('badge_width_fraction'):
        lines.append(f"  badge_width_fraction: {cfg['badge_width_fraction']}")
    if cfg.get('badge_height_fraction'):
        lines.append(f"  badge_height_fraction: {cfg['badge_height_fraction']}")
    if cfg.get('tab_colors'):
        lines.append('tab_colors:')
        for c in cfg['tab_colors']:
            lines.append(f'  - {c}')
    lines.append('repos:')
    for r in cfg['repos']:
        lines.append(f'  - {r}')
    lines.append('')

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write('\n'.join(lines))
