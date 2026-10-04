"""
pixelcraft.palette
Curated color palettes and color utilities optimized for pixel art and AI generation.
"""

from typing import Dict, List, Optional, Tuple, Union
import colorsys

RGBA = Tuple[int, int, int, int]
ColorInput = Union[str, Tuple[int, int, int], Tuple[int, int, int, int], None]


PALETTE_PICO8 = {
    "black": "#000000",
    "dark_blue": "#1D2B53",
    "dark_purple": "#7E2553",
    "dark_green": "#008751",
    "brown": "#AB5236",
    "dark_gray": "#5F574F",
    "light_gray": "#C2C3C7",
    "white": "#FFF1E8",
    "red": "#FF004D",
    "orange": "#FFA300",
    "yellow": "#FFEC27",
    "green": "#00E436",
    "blue": "#29ADFF",
    "indigo": "#83769C",
    "pink": "#FF77A8",
    "peach": "#FFCCAA",
}

PALETTE_DB16 = {
    "black": "#140c1c",
    "dark_purple": "#442434",
    "dark_blue": "#30346d",
    "dark_gray": "#4e4a4e",
    "brown": "#854c30",
    "dark_green": "#346524",
    "red": "#d04648",
    "gray": "#757161",
    "blue": "#597dce",
    "orange": "#d27d2c",
    "light_gray": "#8595a1",
    "light_green": "#6daa2c",
    "peach": "#d2aa99",
    "cyan": "#6dc2ca",
    "yellow": "#dad45e",
    "white": "#deeed6",
}

PALETTE_DB32 = {
    "black": "#000000",
    "dark_blue": "#222034",
    "dark_purple": "#523b40",
    "charcoal": "#45283c",
    "deep_red": "#663931",
    "navy": "#3f3f74",
    "slate_blue": "#306082",
    "teal": "#5b6ee1",
    "sky_blue": "#639bff",
    "cyan": "#5fcde4",
    "bright_cyan": "#cbdbfc",
    "white": "#ffffff",
    "silver": "#9badb7",
    "gray": "#847e87",
    "dark_gray": "#696a6a",
    "purple": "#595652",
    "brick_brown": "#76428a",
    "violet": "#ac3232",
    "crimson": "#d95763",
    "salmon": "#d77643",
    "orange": "#edad54",
    "amber": "#fbf236",
    "yellow": "#8f974a",
    "olive": "#4b692f",
    "forest_green": "#524b24",
    "mud_green": "#323c39",
    "deep_green": "#3f773b",
    "green": "#69b764",
    "lime": "#99e550",
    "khaki": "#d4e68e",
    "sand": "#b86f50",
    "tan": "#e4a672",
}

PALETTE_EDG32 = {
    "deep_black": "#be4a2f",
    "dark_maroon": "#d77643",
    "burnt_orange": "#ead4aa",
    "gold": "#e4a672",
    "peach": "#b86f50",
    "earth": "#733e39",
    "dark_earth": "#3e2731",
    "shadow_purple": "#a22633",
    "ruby": "#e43b44",
    "coral": "#f77622",
    "lemon": "#feae34",
    "banana": "#fee761",
    "lime": "#63c74d",
    "green": "#3e8948",
    "deep_green": "#265c42",
    "sea_dark": "#193c3e",
    "midnight": "#124e89",
    "sea_blue": "#0099db",
    "sky": "#2ce8f5",
    "cloud": "#ffffff",
    "light_gray": "#c0cbdc",
    "steel": "#8b9bb4",
    "slate": "#5a6988",
    "ink": "#3a4466",
    "night": "#262b44",
    "obsidian": "#181425",
    "plum": "#ff0044",
    "pink": "#68386c",
    "mauve": "#b55088",
    "magenta": "#f6757a",
    "rose": "#e8b796",
    "cream": "#c28569",
}

PALETTE_GAMEBOY = {
    "darkest": "#0f380f",
    "dark": "#306230",
    "light": "#8bac0f",
    "lightest": "#9bbc0f",
}

PALETTE_SWEETIE16 = {
    "dark_purple": "#1a1c2c",
    "navy": "#5d275d",
    "wine": "#b13e53",
    "coral": "#ef7d57",
    "orange": "#ffcd75",
    "lime": "#a7f070",
    "green": "#38b764",
    "dark_green": "#257179",
    "dark_blue": "#29366f",
    "blue": "#3b5dc9",
    "light_blue": "#41a6f6",
    "cyan": "#73eff7",
    "white": "#f4f4f4",
    "silver": "#94b0c2",
    "gray": "#566c86",
    "charcoal": "#333c57",
}

BUILTIN_PALETTES = {
    "pico8": PALETTE_PICO8,
    "db16": PALETTE_DB16,
    "dawnbringer16": PALETTE_DB16,
    "db32": PALETTE_DB32,
    "dawnbringer32": PALETTE_DB32,
    "edg32": PALETTE_EDG32,
    "endesga32": PALETTE_EDG32,
    "gameboy": PALETTE_GAMEBOY,
    "sweetie16": PALETTE_SWEETIE16,
}


def hex_to_rgba(hex_str: str) -> RGBA:
    """Convert hex color string (#RGB, #RRGGBB, #RRGGBBAA) to (R, G, B, A) tuple."""
    hex_clean = hex_str.strip().lstrip("#")
    if len(hex_clean) == 3:
        r = int(hex_clean[0] * 2, 16)
        g = int(hex_clean[1] * 2, 16)
        b = int(hex_clean[2] * 2, 16)
        return (r, g, b, 255)
    elif len(hex_clean) == 4:
        r = int(hex_clean[0] * 2, 16)
        g = int(hex_clean[1] * 2, 16)
        b = int(hex_clean[2] * 2, 16)
        a = int(hex_clean[3] * 2, 16)
        return (r, g, b, a)
    elif len(hex_clean) == 6:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        return (r, g, b, 255)
    elif len(hex_clean) == 8:
        r = int(hex_clean[0:2], 16)
        g = int(hex_clean[2:4], 16)
        b = int(hex_clean[4:6], 16)
        a = int(hex_clean[6:8], 16)
        return (r, g, b, a)
    raise ValueError(f"Invalid hex color format: '{hex_str}'")


def rgba_to_hex(rgba: RGBA, include_alpha: bool = False) -> str:
    """Convert RGBA tuple (0-255) to hex string."""
    r, g, b, a = rgba
    if include_alpha and a < 255:
        return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
    return f"#{r:02x}{g:02x}{b:02x}"


def parse_color(color: ColorInput) -> Optional[RGBA]:
    """Parse any flexible color input into an RGBA tuple, or None for transparent."""
    if color is None:
        return None
    if isinstance(color, str):
        c_lower = color.strip().lower()
        if c_lower in ("transparent", "none", "", "."):
            return None
        if c_lower.startswith("#"):
            return hex_to_rgba(c_lower)
        standard_names = {
            "black": (0, 0, 0, 255),
            "white": (255, 255, 255, 255),
            "red": (255, 0, 0, 255),
            "green": (0, 255, 0, 255),
            "blue": (0, 0, 255, 255),
            "yellow": (255, 255, 0, 255),
            "cyan": (0, 255, 255, 255),
            "magenta": (255, 0, 255, 255),
            "orange": (255, 165, 0, 255),
            "purple": (128, 0, 128, 255),
            "pink": (255, 192, 203, 255),
            "brown": (139, 69, 19, 255),
            "gold": (255, 215, 0, 255),
            "silver": (192, 192, 192, 255),
            "gray": (128, 128, 128, 255),
            "grey": (128, 128, 128, 255),
            "light_gray": (200, 200, 200, 255),
            "light_grey": (200, 200, 200, 255),
            "dark_gray": (64, 64, 64, 255),
            "dark_grey": (64, 64, 64, 255),
        }
        if c_lower in standard_names:
            return standard_names[c_lower]
        raise ValueError(f"Unrecognized color string: '{color}'. Use hex '#rrggbb' or a registered palette.")
    if isinstance(color, (tuple, list)):
        if len(color) == 3:
            return (int(color[0]), int(color[1]), int(color[2]), 255)
        elif len(color) == 4:
            return (int(color[0]), int(color[1]), int(color[2]), int(color[3]))
        raise ValueError(f"Color tuple must have 3 or 4 values, got {len(color)}")
    raise TypeError(f"Unsupported color type: {type(color)}")


class Palette:
    """
    Manages a collection of colors and key-to-color bindings for sprites.
    Supports easy ASCII character mapping, ramp generation, and named color lookups.
    """

    def __init__(self, colors: Optional[Dict[str, ColorInput]] = None):
        self._map: Dict[str, Optional[RGBA]] = {}
        self._map["."] = None
        self._map[" "] = None

        if colors:
            for key, val in colors.items():
                self.add(key, val)

    @classmethod
    def load(cls, name: str) -> "Palette":
        """Load one of the curated built-in palettes: 'pico8', 'db16', 'db32', 'edg32', 'gameboy', 'sweetie16'."""
        name_clean = name.strip().lower()
        if name_clean not in BUILTIN_PALETTES:
            available = ", ".join(BUILTIN_PALETTES.keys())
            raise ValueError(f"Unknown palette '{name}'. Available: {available}")
        return cls(BUILTIN_PALETTES[name_clean])

    def add(self, key: str, color: ColorInput) -> "Palette":
        """Add or overwrite a color mapped to a key (character or name)."""
        self._map[key] = parse_color(color)
        return self

    def with_aliases(self, mapping: Dict[str, Union[str, ColorInput]]) -> "Palette":
        """
        Create a new Palette with additional aliases (e.g. mapping single characters to existing palette names or hex).
        Example: palette.with_aliases({'#': 'dark_purple', 'O': 'peach', 'R': 'red'})
        """
        new_palette = Palette()
        new_palette._map = dict(self._map)
        for char_key, target in mapping.items():
            if isinstance(target, str) and target in self._map:
                new_palette._map[char_key] = self._map[target]
            else:
                new_palette._map[char_key] = parse_color(target)
        return new_palette

    def get(self, key: str) -> Optional[RGBA]:
        """Get RGBA tuple for a key, or None if transparent. Raises KeyError if missing."""
        if key in self._map:
            return self._map[key]
        if key.startswith("#"):
            return hex_to_rgba(key)
        raise KeyError(f"Key '{key}' not found in palette. Registered keys: {list(self._map.keys())}")

    def has(self, key: str) -> bool:
        return key in self._map

    def keys(self) -> List[str]:
        return list(self._map.keys())

    @staticmethod
    def create_ramp(
        base_color: ColorInput,
        steps: int = 4,
        darken_factor: float = 0.5,
        brighten_factor: float = 0.4,
        hue_shift_deg: float = 0.0,
    ) -> List[RGBA]:
        """
        Generate a smooth color ramp (highlight -> base -> shadow) for shading pixel art.
        hue_shift_deg: Shift hue towards yellow/warm in highlights and blue/cold in shadows.
        """
        base_rgba = parse_color(base_color)
        if not base_rgba:
            raise ValueError("Base color cannot be transparent.")

        r, g, b, a = base_rgba
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)

        ramp: List[RGBA] = []
        for i in range(steps):
            if steps == 1:
                t = 0.0
            else:
                t = -1.0 + (2.0 * i / (steps - 1))

            if t < 0:
                new_l = max(0.0, l * (1.0 + t * darken_factor))
                new_h = (h - (abs(t) * hue_shift_deg / 360.0)) % 1.0
            else:
                new_l = min(1.0, l + ((1.0 - l) * t * brighten_factor))
                new_h = (h + (t * hue_shift_deg / 360.0)) % 1.0

            nr, ng, nb = colorsys.hls_to_rgb(new_h, new_l, s)
            ramp.append((int(nr * 255), int(ng * 255), int(nb * 255), a))

        return ramp

    def __repr__(self) -> str:
        return f"<Palette colors={len(self._map)} keys={list(self._map.keys())[:8]}...>"
