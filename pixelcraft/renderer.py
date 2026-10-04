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


def export_gallery(
    target_dir: Union[str, Path] = "output",
    output_html_path: Optional[Union[str, Path]] = None,
    title: str = "PixelCraft Sprite Showcase",
) -> Path:
    """
    Scans a directory for generated sprite assets (.png, .gif) and generates an interactive HTML showcase gallery.
    Features:
    - Interactive zoom selector (1x, 2x, 4x, 6x, 8x, 12x)
    - Background switcher (checkerboard, dark, light, green)
    - Search / filter input
    - Responsive grid displaying dimensions and filenames
    - Pure client-side HTML/CSS/JS with zero external dependencies
    """
    directory = Path(target_dir)
    if not output_html_path:
        out_path = directory / "gallery.html"
    else:
        out_path = Path(output_html_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    candidates = []
    for ext in ("*.png", "*.gif"):
        for f in directory.rglob(ext):
            if f.name.endswith("_preview.png") or f.name.endswith("_preview.gif"):
                continue
            if f.resolve() == out_path.resolve():
                continue
            candidates.append(f)

    candidates = sorted(set(candidates), key=lambda x: str(x).lower())

    cards_html = []
    for img_path in candidates:
        try:
            rel_src = img_path.relative_to(out_path.parent).as_posix()
        except ValueError:
            rel_src = img_path.as_posix()

        name = img_path.name
        is_gif = img_path.suffix.lower() == ".gif"
        badge = "ANIMATED GIF" if is_gif else "PNG SPRITE"
        badge_color = "#f48c06" if is_gif else "#4895ef"

        dim_str = ""
        try:
            with Image.open(img_path) as im:
                dim_str = f"{im.width}x{im.height}px"
        except Exception:
            dim_str = ""

        pill_text = f"{dim_str} &bull; {badge}" if dim_str else badge

        card = f"""      <div class="card" data-name="{name.lower()}">
        <div class="card-header">
          <span class="card-title" title="{name}">{name}</span>
          <span class="badge" style="color: {badge_color}; border-color: {badge_color}44; background: {badge_color}18;">{pill_text}</span>
        </div>
        <div class="viewport checkerboard">
          <img class="sprite-img" src="{rel_src}" alt="{name}" loading="lazy" />
        </div>
        <div class="card-footer">
          <code>{rel_src}</code>
        </div>
      </div>"""
        cards_html.append(card)

    cards_block = "\\n".join(cards_html) if cards_html else '<p style="color:#888; text-align:center; padding:40px;">No sprites found in directory.</p>'

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 24px 32px;
    background: #0f111a;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  }}
  header {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #1e2235;
  }}
  .brand {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .brand h1 {{
    margin: 0;
    font-size: 1.4rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .counter {{
    font-size: 0.85rem;
    color: #94a3b8;
    background: #1e2235;
    padding: 4px 10px;
    border-radius: 999px;
  }}
  .toolbar {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    align-items: center;
  }}
  .control-group {{
    display: flex;
    align-items: center;
    gap: 6px;
    background: #181b29;
    padding: 4px 8px;
    border-radius: 8px;
    border: 1px solid #282d44;
  }}
  .control-group label {{
    font-size: 0.75rem;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
  }}
  button, select, input {{
    background: #23283c;
    color: #f1f5f9;
    border: 1px solid #333a56;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 0.85rem;
    cursor: pointer;
    outline: none;
    transition: all 0.15s ease;
  }}
  button:hover, select:hover {{
    background: #2d334d;
    border-color: #4f587d;
  }}
  input[type="text"] {{
    cursor: text;
    width: 180px;
  }}
  input[type="text"]:focus {{
    border-color: #60a5fa;
    box-shadow: 0 0 0 2px #60a5fa33;
  }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
  }}
  .card {{
    background: #151824;
    border: 1px solid #23283c;
    border-radius: 12px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    transition: transform 0.15s ease, border-color 0.15s ease;
  }}
  .card:hover {{
    transform: translateY(-2px);
    border-color: #3b4363;
  }}
  .card-header {{
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    background: #191c2b;
    border-bottom: 1px solid #23283c;
  }}
  .card-title {{
    font-size: 0.9rem;
    font-weight: 600;
    color: #e2e8f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .badge {{
    font-size: 0.7rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 999px;
    border: 1px solid transparent;
    flex-shrink: 0;
  }}
  .viewport {{
    min-height: 200px;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    position: relative;
    overflow: hidden;
  }}
  .viewport.checkerboard {{
    background-color: #1a1c26;
    background-image:
      linear-gradient(45deg, #13151f 25%, transparent 25%),
      linear-gradient(-45deg, #13151f 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #13151f 75%),
      linear-gradient(-45deg, transparent 75%, #13151f 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
  }}
  .viewport.dark {{ background: #08080c; }}
  .viewport.light {{ background: #f1f5f9; }}
  .viewport.green {{ background: #00ff00; }}
  .sprite-img {{
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    transform-origin: center;
    transition: transform 0.1s ease;
    display: block;
  }}
  .card-footer {{
    padding: 10px 16px;
    background: #131520;
    border-top: 1px solid #1e2235;
    font-size: 0.75rem;
    color: #64748b;
  }}
  .card-footer code {{
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    word-break: break-all;
  }}
</style>
</head>
<body>
  <header>
    <div class="brand">
      <h1>{title}</h1>
      <span class="counter" id="item-count">{len(candidates)} sprites</span>
    </div>
    <div class="toolbar">
      <div class="control-group">
        <label>Search</label>
        <input type="text" id="search-box" placeholder="Filter sprites..." oninput="filterSprites()" />
      </div>
      <div class="control-group">
        <label>Zoom</label>
        <select id="zoom-select" onchange="setZoom(this.value)">
          <option value="1">1x</option>
          <option value="2">2x</option>
          <option value="4" selected>4x</option>
          <option value="6">6x</option>
          <option value="8">8x</option>
          <option value="12">12x</option>
        </select>
      </div>
      <div class="control-group">
        <label>Background</label>
        <select onchange="setBackground(this.value)">
          <option value="checkerboard" selected>Checkerboard</option>
          <option value="dark">Deep Dark</option>
          <option value="light">Light</option>
          <option value="green">Chroma Green</option>
        </select>
      </div>
    </div>
  </header>

  <div class="grid" id="sprites-grid">
{cards_block}
  </div>

<script>
  let currentZoom = 4;
  function setZoom(val) {{
    currentZoom = Number(val);
    document.querySelectorAll('.sprite-img').forEach(img => {{
      img.style.transform = `scale(${{currentZoom}})`;
    }});
  }}
  function setBackground(cls) {{
    document.querySelectorAll('.viewport').forEach(vp => {{
      vp.className = `viewport ${{cls}}`;
    }});
  }}
  function filterSprites() {{
    const q = document.getElementById('search-box').value.toLowerCase();
    let visible = 0;
    document.querySelectorAll('.card').forEach(card => {{
      const match = card.getAttribute('data-name').includes(q);
      card.style.display = match ? 'flex' : 'none';
      if (match) visible++;
    }});
    document.getElementById('item-count').innerText = `${{visible}} sprites`;
  }}
  window.addEventListener('DOMContentLoaded', () => {{
    setZoom(document.getElementById('zoom-select').value);
  }});
</script>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return out_path

