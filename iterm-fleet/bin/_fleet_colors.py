"""Shared named-color palette for iterm-fleet tools (tab colors, badge color)."""

NAMED_COLORS = {
    'red':    (0.75, 0.25, 0.25),
    'blue':   (0.25, 0.50, 0.80),
    'green':  (0.20, 0.65, 0.40),
    'amber':  (0.80, 0.60, 0.15),
    'orange': (0.85, 0.40, 0.10),
    'teal':   (0.30, 0.65, 0.70),
    'purple': (0.55, 0.25, 0.75),
    'olive':  (0.60, 0.60, 0.20),
    'gray':   (0.55, 0.55, 0.55),
    'grey':   (0.55, 0.55, 0.55),
    'cyan':   (0.25, 0.70, 0.75),
    'pink':   (0.85, 0.45, 0.65),
    'yellow': (0.85, 0.75, 0.20),
    'white':  (0.85, 0.85, 0.85),
}

DEFAULT_TAB_PALETTE = ['red', 'blue', 'green', 'amber', 'orange', 'teal', 'purple', 'olive']


def parse_color(spec):
    """Parse a color spec: a named color, or 'r,g,b' floats in [0,1]. Raises ValueError."""
    spec = spec.strip().lower()
    if spec in NAMED_COLORS:
        return NAMED_COLORS[spec]
    parts = spec.split(',')
    if len(parts) == 3:
        try:
            r, g, b = (float(p) for p in parts)
            if all(0.0 <= c <= 1.0 for c in (r, g, b)):
                return (r, g, b)
        except ValueError:
            pass
    raise ValueError(
        f"invalid color '{spec}' — use a name ({', '.join(sorted(set(NAMED_COLORS) - {'grey'}))}) "
        "or 'r,g,b' floats between 0 and 1"
    )


def rgb_dict(r, g, b, alpha=1.0):
    return {
        'Red Component': float(r),
        'Green Component': float(g),
        'Blue Component': float(b),
        'Alpha Component': float(alpha),
        'Color Space': 'sRGB',
    }
