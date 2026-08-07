"""Shared iTerm2 preferences access for iterm-fleet tools.

Reads/writes the live com.googlecode.iterm2 defaults domain. Font changes
apply to the named *profile* (global to the whole app, not scoped to fleet
panes) since a session's font must come from a real, matching profile — see
fleet-build's minimal_session_view docstring for why the Guid link itself
must stay synthetic.
"""
import subprocess
import plistlib

DOMAIN = 'com.googlecode.iterm2'


def _read_defaults():
    out = subprocess.run(['defaults', 'export', DOMAIN, '-'],
                          capture_output=True, timeout=5, check=True)
    return plistlib.loads(out.stdout)


def _write_defaults(data):
    payload = plistlib.dumps(data, fmt=plistlib.FMT_XML)
    subprocess.run(['defaults', 'import', DOMAIN, '-'], input=payload, timeout=5, check=True)


def lookup_profile(name):
    """Return (guid, font_string, point_size) for the named iTerm2 profile,
    or (None, 'Menlo 13', 13.0) if it can't be found (non-macOS, no iTerm2
    preferences yet, etc.)."""
    try:
        data = _read_defaults()
        for bm in data.get('New Bookmarks', []):
            if bm.get('Name') == name:
                font = bm.get('Normal Font', 'Menlo 13')
                size = float(font.rsplit(' ', 1)[-1])
                return bm.get('Guid'), font, size
    except Exception:
        pass
    return None, 'Menlo 13', 13.0


def set_profile_font(name, size, family=None):
    """Update Normal Font (and Non Ascii Font, if set) for the named profile
    in place, leaving every other preference untouched. Returns the new font
    string. Raises ValueError if no profile with that name exists."""
    size_str = str(int(size)) if float(size).is_integer() else str(size)
    data = _read_defaults()
    new_font = None
    for bm in data.get('New Bookmarks', []):
        if bm.get('Name') == name:
            current = bm.get('Normal Font', 'Menlo 13')
            fam = family or current.rsplit(' ', 1)[0]
            new_font = f'{fam} {size_str}'
            bm['Normal Font'] = new_font
            if 'Non Ascii Font' in bm:
                nfam = family or bm['Non Ascii Font'].rsplit(' ', 1)[0]
                bm['Non Ascii Font'] = f'{nfam} {size}'
    if new_font is None:
        raise ValueError(f"no iTerm2 profile named '{name}' found")
    _write_defaults(data)
    return new_font


def set_badge_fractions(width_fraction, height_fraction):
    """Set the global badge max-size preferences (iTerm2 has no per-profile
    or per-session badge size key — this is app-wide)."""
    subprocess.run(['defaults', 'write', DOMAIN, 'BadgeMaxWidthFraction',
                     '-float', str(width_fraction)], check=True)
    subprocess.run(['defaults', 'write', DOMAIN, 'BadgeMaxHeightFraction',
                     '-float', str(height_fraction)], check=True)
