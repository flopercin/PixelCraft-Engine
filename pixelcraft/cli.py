"""
pixelcraft.cli
Command-line interface for PixelCraft.
Supports rendering scripts, previewing images directly in terminal with ANSI colors,
listing palettes, and running linter diagnostics.
"""

import sys
import argparse
from pathlib import Path
from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from .palette import BUILTIN_PALETTES
from .canvas import Canvas
from .renderer import render_ansi, print_ansi
from .linter import lint_sprite


def cli_preview_image(image_path: str, max_width: int = 64):
    """Load an existing PNG/image and render it in terminal ANSI TrueColor."""
    path = Path(image_path)
    if not path.exists():
        print(f"Error: File '{image_path}' not found.")
        sys.exit(1)

    img = Image.open(path).convert("RGBA")
    w, h = img.size
    if w > max_width:
        scale = max_width / float(w)
        new_h = max(1, int(h * scale))
        img = img.resize((max_width, new_h), Image.Resampling.NEAREST)
        w, h = img.size

    c = Canvas(w, h)
    for y in range(h):
        for x in range(w):
            r, g, b, a = img.getpixel((x, y))
            if a > 10:
                c.set_pixel(x, y, (r, g, b, a))

    print_ansi(c, title=f"{path.name} ({w}x{h})")
    rep = lint_sprite(c)
    print(rep.summary())


def cli_list_palettes():
    """Print all available built-in palettes and color counts."""
    print("\n=== Available Curated Pixel Art Palettes ===")
    for name, p in BUILTIN_PALETTES.items():
        print(f"  • {name.ljust(15)} ({len(p)} colors)")
    print("\nTip: Use Palette.load('name') in Python to load any of these palettes.")


def main():
    parser = argparse.ArgumentParser(description="PixelCraft - AI Pixel Art Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    preview_parser = subparsers.add_parser("preview", help="Preview any PNG/image directly in terminal")
    preview_parser.add_argument("path", help="Path to image file")
    preview_parser.add_argument("--max-width", type=int, default=48, help="Max width for terminal display")

    subparsers.add_parser("palettes", help="List built-in color palettes")

    gallery_parser = subparsers.add_parser("gallery", help="Generate an interactive HTML showcase gallery for sprites")
    gallery_parser.add_argument("dir", nargs="?", default="output", help="Directory containing sprites (default: output)")
    gallery_parser.add_argument("-o", "--output", default=None, help="Output HTML file path (default: <dir>/gallery.html)")

    args = parser.parse_args()

    if args.command == "preview":
        cli_preview_image(args.path, args.max_width)
    elif args.command == "palettes":
        cli_list_palettes()
    elif args.command == "gallery":
        from .renderer import export_gallery
        out = export_gallery(args.dir, args.output)
        print(f"Gallery generated: {out}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
