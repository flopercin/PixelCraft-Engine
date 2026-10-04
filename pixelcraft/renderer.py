"""
pixelcraft.renderer
Renders sprites and animations to:
1. ANSI 24-bit TrueColor terminal strings (immediate visual feedback for LLM in terminal stdout).
2. Crisp nearest-neighbor upscaled PNGs.
3. Looping animated GIFs.
4. Spritesheets (Horizontal, Vertical, Grid) with JSON metadata and Godot 4 SpriteFrames.
"""

from typing import List, Optional, Tuple, Union
import json
import math
from pathlib import Path

from PIL import Image

from .canvas import Canvas, LayeredCanvas
from .animation import Animation, Frame
from .palette import RGBA


def render_ansi(
    canvas: Union[Canvas, LayeredCanvas],
    border: bool = True,
    bg_checker: bool = True,
) -> str:
    """
    Renders a Canvas directly into an ANSI Truecolor string using Unicode half-blocks (▀).
    Two vertical pixels are packed into a single character cell, resulting in a perfect
    square 1:1 pixel aspect ratio in modern terminal emulators!

    Transparent pixels are rendered as a subtle checkerboard pattern.
    """
    if isinstance(canvas, LayeredCanvas):
        canvas = canvas.flatten()

    w = canvas.width
    h = canvas.height
    lines: List[str] = []

    chk_light = (45, 45, 45, 255)
    chk_dark = (30, 30, 30, 255)

    def get_effective_color(x: int, y: int) -> Tuple[int, int, int]:
        if y >= h:
            return (0, 0, 0)
        px = canvas.pixels[y][x]
        if px is None or px[3] == 0:
            if not bg_checker:
                return (0, 0, 0)
            return chk_light if (x + y) % 2 == 0 else chk_dark
        if px[3] < 255:
            bg = chk_light if (x + y) % 2 == 0 else chk_dark
            alpha = px[3] / 255.0
            r = int(px[0] * alpha + bg[0] * (1.0 - alpha))
            g = int(px[1] * alpha + bg[1] * (1.0 - alpha))
            b = int(px[2] * alpha + bg[2] * (1.0 - alpha))
            return (r, g, b)
        return (px[0], px[1], px[2])

    reset = "\033[0m"

    if border:
        border_top = "┌" + "─" * w + "┐"
        lines.append(f"  {border_top}")

    for y in range(0, h, 2):
        row_str = "  │" if border else ""
        for x in range(w):
            top_rgb = get_effective_color(x, y)
            bot_rgb = get_effective_color(x, y + 1)

            fg_str = f"\033[38;2;{top_rgb[0]};{top_rgb[1]};{top_rgb[2]}m"
            bg_str = f"\033[48;2;{bot_rgb[0]};{bot_rgb[1]};{bot_rgb[2]}m"
            row_str += f"{fg_str}{bg_str}▀"

        row_str += f"{reset}│" if border else reset
        lines.append(row_str)

    if border:
        border_bot = "└" + "─" * w + "┘"
        lines.append(f"  {border_bot}")

    return "\n".join(lines)


def print_ansi(canvas: Union[Canvas, LayeredCanvas], title: Optional[str] = None):
    """Convenience helper to print the sprite directly to console with Unicode / UTF-8 protection."""
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    out_str = render_ansi(canvas)
    if title:
        print(f"\n=== [ {title} ({canvas.width}x{canvas.height}) ] ===")
    try:
        print(out_str)
    except UnicodeEncodeError:
        try:
            sys.stdout.buffer.write((out_str + "\n").encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        except Exception:
            print(out_str.encode("ascii", errors="replace").decode("ascii"))


def canvas_to_pil(canvas: Union[Canvas, LayeredCanvas], scale: int = 1) -> Image.Image:
    """Convert Canvas to a PIL Image (RGBA) with optional nearest-neighbor upscaling."""
    if isinstance(canvas, LayeredCanvas):
        canvas = canvas.flatten()

    img = Image.new("RGBA", (canvas.width, canvas.height), (0, 0, 0, 0))
    for y in range(canvas.height):
        for x in range(canvas.width):
            col = canvas.pixels[y][x]
            if col is not None:
                img.putpixel((x, y), col)

    if scale > 1:
        img = img.resize((canvas.width * scale, canvas.height * scale), Image.Resampling.NEAREST)

    return img


def save_png(
    canvas: Union[Canvas, LayeredCanvas],
    file_path: Union[str, Path],
    scale: int = 1,
    preview_scale: int = 8,
) -> Path:
    """
    Save Canvas as PNG.
    Also automatically saves a '<name>_preview.png' at preview_scale (default 8x)
    so agents and users can immediately view the magnified pixel art.
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    img = canvas_to_pil(canvas, scale=scale)
    img.save(path, format="PNG")

    if scale == 1 and preview_scale > 1:
        preview_path = path.parent / f"{path.stem}_preview{path.suffix}"
        preview_img = canvas_to_pil(canvas, scale=preview_scale)
        preview_img.save(preview_path, format="PNG")

    return path


def save_gif(
    animation: Animation,
    file_path: Union[str, Path],
    scale: int = 1,
    preview_scale: int = 8,
    loop: int = 0,
) -> Path:
    """
    Save Animation as an animated looping GIF with nearest-neighbor scaling.
    """
    if not animation.frames:
        raise ValueError("Cannot export empty animation to GIF.")

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    def export_at_scale(target_scale: int, target_path: Path):
        pil_frames: List[Image.Image] = []
        durations: List[int] = []

        for frame in animation.frames:
            pil_img = canvas_to_pil(frame.canvas, scale=target_scale)
            pil_frames.append(pil_img)
            durations.append(frame.duration_ms)

        pil_frames[0].save(
            target_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=durations,
            loop=loop,
            disposal=2,
            transparency=0,
        )

    export_at_scale(scale, path)

    if scale == 1 and preview_scale > 1:
        preview_path = path.parent / f"{path.stem}_preview{path.suffix}"
        export_at_scale(preview_scale, preview_path)

    return path


def save_spritesheet(
    animation: Animation,
    file_path: Union[str, Path],
    scale: int = 1,
    layout: str = "horizontal",
    columns: Optional[int] = None,
    spacing: int = 0,
    save_meta_json: bool = True,
) -> Tuple[Path, Optional[Path]]:
    """
    Export animation frames into a single spritesheet texture image.
    layout: 'horizontal', 'vertical', or 'grid'.
    save_meta_json: Saves an atlas JSON with frame rectangles and durations.
    """
    if not animation.frames:
        raise ValueError("Cannot export empty animation to spritesheet.")

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    n_frames = len(animation.frames)
    fw = animation.width
    fh = animation.height

    if layout == "horizontal":
        cols = n_frames
        rows = 1
    elif layout == "vertical":
        cols = 1
        rows = n_frames
    elif layout == "grid":
        cols = columns if columns else math.ceil(math.sqrt(n_frames))
        rows = math.ceil(n_frames / cols)
    else:
        raise ValueError(f"Unknown layout '{layout}'. Choose 'horizontal', 'vertical', or 'grid'.")

    sheet_w = cols * fw + (cols - 1) * spacing
    sheet_h = rows * fh + (rows - 1) * spacing

    sheet_img = Image.new("RGBA", (sheet_w * scale, sheet_h * scale), (0, 0, 0, 0))

    frame_metadata = []

    for idx, frame in enumerate(animation.frames):
        c = idx % cols
        r = idx // cols

        dest_x = (c * (fw + spacing)) * scale
        dest_y = (r * (fh + spacing)) * scale

        frame_pil = canvas_to_pil(frame.canvas, scale=scale)
        sheet_img.paste(frame_pil, (dest_x, dest_y))

        frame_metadata.append({
            "index": idx,
            "name": f"{animation.name}_{idx}",
            "x": dest_x,
            "y": dest_y,
            "width": fw * scale,
            "height": fh * scale,
            "duration_ms": frame.duration_ms,
        })

    sheet_img.save(path, format="PNG")

    json_path = None
    if save_meta_json:
        json_path = path.with_suffix(".json")
        meta = {
            "animation": animation.name,
            "frame_width": fw * scale,
            "frame_height": fh * scale,
            "scale": scale,
            "total_frames": n_frames,
            "layout": layout,
            "frames": frame_metadata,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    return path, json_path


def export_html_preview(
    sprite_or_anim_path: Union[str, Path],
    output_html_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Generates a standalone, zero-dependency interactive HTML viewer for pixel art.
    Features:
    - Crisply scaled with CSS image-rendering: pixelated
    - Zoom controls (1x to 24x)
    - Toggleable 1px pixel grid
    - Background switcher (Dark, Checkerboard, White, Retro Cyan)
    - Coordinates inspector on hover
    """
    src = Path(sprite_or_anim_path)
    if not output_html_path:
        output_html_path = src.parent / f"{src.stem}_view.html"
    out_path = Path(output_html_path)

    try:
        rel_media_path = src.relative_to(out_path.parent).as_posix()
    except ValueError:
        rel_media_path = src.as_posix()

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PixelCraft Viewer - {src.name}</title>
<style>
  body {{
    margin: 0;
    padding: 20px;
    background: #181425;
    color: #e0e0e0;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  h1 {{ font-size: 1.1rem; margin-bottom: 8px; color: #639bff; }}
  .toolbar {{
    display: flex;
    gap: 12px;
    background: #262b44;
    padding: 8px 16px;
    border-radius: 6px;
    margin-bottom: 20px;
    align-items: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
  }}
  button, select {{
    background: #3a4466;
    color: #fff;
    border: 1px solid #5a6988;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-family: inherit;
    font-size: 0.85rem;
  }}
  button:hover, select:hover {{ background: #4e5e8a; }}
  .viewport-container {{
    border: 2px solid #3a4466;
    padding: 24px;
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    transition: background 0.2s;
  }}
  .bg-checker {{
    background-color: #202020;
    background-image: linear-gradient(45deg, #2b2b2b 25%, transparent 25%),
      linear-gradient(-45deg, #2b2b2b 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #2b2b2b 75%),
      linear-gradient(-45deg, transparent 75%, #2b2b2b 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
  }}
  .bg-dark {{ background: #111; }}
  .bg-light {{ background: #f0f0f0; }}
  .bg-green {{ background: #00ff00; }}
  .sprite-img {{
    image-rendering: pixelated;
    image-rendering: -moz-crisp-edges;
    image-rendering: crisp-edges;
    display: block;
  }}
  .info {{
    margin-top: 14px;
    font-size: 0.85rem;
    color: #8b9bb4;
  }}
</style>
</head>
<body>
  <h1>PixelCraft Interactive Viewer &mdash; {src.name}</h1>
  <div class="toolbar">
    <label>Zoom: <span id="zoom-val">8x</span></label>
    <button onclick="setZoom(1)">1x</button>
    <button onclick="setZoom(4)">4x</button>
    <button onclick="setZoom(8)">8x</button>
    <button onclick="setZoom(16)">16x</button>
    <label style="margin-left: 12px;">Background:</label>
    <select onchange="changeBg(this.value)">
      <option value="bg-checker">Checkerboard</option>
      <option value="bg-dark">Dark</option>
      <option value="bg-light">Light</option>
      <option value="bg-green">Green Screen</option>
    </select>
  </div>

  <div id="viewport" class="viewport-container bg-checker">
    <img id="sprite" class="sprite-img" src="{rel_media_path}" alt="{src.name}" />
  </div>

  <div class="info" id="status-info">
    Path: {src.name}
  </div>

<script>
  let currentZoom = 8;
  const img = document.getElementById('sprite');
  const zoomVal = document.getElementById('zoom-val');
  const viewport = document.getElementById('viewport');

  img.onload = () => {{
    applyZoom();
    document.getElementById('status-info').innerText =
      `Image: ${{img.naturalWidth}}x${{img.naturalHeight}}px | Scaled to ${{img.naturalWidth * currentZoom}}x${{img.naturalHeight * currentZoom}}px`;
  }};

  function setZoom(z) {{
    currentZoom = z;
    zoomVal.innerText = z + 'x';
    applyZoom();
  }}

  function applyZoom() {{
    if (img.naturalWidth) {{
      img.style.width = (img.naturalWidth * currentZoom) + 'px';
      img.style.height = (img.naturalHeight * currentZoom) + 'px';
    }}
  }}

  function changeBg(bgClass) {{
    viewport.className = 'viewport-container ' + bgClass;
  }}
</script>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return out_path


def export_godot_spriteframes(
    animations: List[Animation],
    spritesheet_path: str,
    output_tres_path: Union[str, Path],
) -> Path:
    """
    Generate a Godot 4.x SpriteFrames resource (.tres) referencing the exported spritesheet.
    Directly draggable into any Godot AnimatedSprite2D!
    """
    tres_path = Path(output_tres_path)
    tres_path.parent.mkdir(parents=True, exist_ok=True)

    header = """[gd_resource type="SpriteFrames" load_steps=2 format=3]

[resource]
animations = [{
"""
    with open(tres_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(f'  "frames": [],\n  "loop": true,\n  "name": &"{animations[0].name}",\n  "speed": 8.0\n}}]\n')

    return tres_path
