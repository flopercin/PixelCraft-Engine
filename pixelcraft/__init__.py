"""
PixelCraft - A specialized programmatic pixel art & 2D animation engine designed for AI Agents.
"""

from .palette import Palette, RGBA, ColorInput, parse_color, hex_to_rgba, rgba_to_hex, BUILTIN_PALETTES
from .canvas import Canvas, LayeredCanvas
from .animation import Animation, Frame
from .renderer import (
    render_ansi,
    print_ansi,
    save_png,
    save_gif,
    save_spritesheet,
    export_godot_spriteframes,
    export_html_preview,
)
from .linter import lint_sprite, LintReport

__all__ = [
    "Canvas",
    "LayeredCanvas",
    "Palette",
    "Animation",
    "Frame",
    "RGBA",
    "ColorInput",
    "parse_color",
    "hex_to_rgba",
    "rgba_to_hex",
    "BUILTIN_PALETTES",
    "render_ansi",
    "print_ansi",
    "save_png",
    "save_gif",
    "save_spritesheet",
    "export_godot_spriteframes",
    "export_html_preview",
    "lint_sprite",
    "LintReport",
]
