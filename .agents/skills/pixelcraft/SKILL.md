---
name: pixelcraft
description: >-
  Specialized expert skill for generating retro 2D pixel art sprites, icons, tiles, characters,
  weapons, and frame-by-frame animations using the PixelCraft engine. Prioritizes procedural
  geometric primitives (draw_shaded_sphere, draw_polygon, draw_thick_line, mirror_horizontal)
  for token-efficient, high-quality, zero-drift sprites. Enforces silhouette-first design,
  curated palettes (PICO-8, DB16, DB32, Sweetie16), clean cluster shading, negative space,
  ANSI terminal inspection, visual verification via view_file, and export to PNG, animated GIF,
  and Godot/Unity spritesheets. Trigger keywords: pixelcraft, pixel art, 2D sprite, spritesheet,
  пиксель-арт, спрайт, pixel art code, procedural sprite.
---

# PixelCraft: AI Pixel Art & Animation Skill

This skill teaches the agent how to programmatically generate clean, iconic, readable 2D pixel art sprites and animations using the `pixelcraft` engine.

---

## ⚡ CRITICAL OPERATIONAL DIRECTIVES (DO NOT SKIP)

1. 🏆 **PRIMARY & RECOMMENDED METHOD: PROCEDURAL GEOMETRIC GENERATION**
   * **ALWAYS prefer procedural primitives over ASCII grids** for characters, monsters, weapons, and items.
   * **Why Procedural is Superior:**
     * **Significantly higher artistic quality:** Mathematical lighting (`draw_shaded_sphere`, `draw_shaded_cylinder`) produces real 3D volume, smooth specular highlights, and clean bevels.
     * **4–5x fewer tokens:** A 25-line procedural script uses a fraction of the context window compared to giant 24×24 or 32×32 ASCII text grids.
     * **Zero alignment bugs:** Eliminates off-by-one line length errors and character drift.
   * *ASCII grids are only a secondary fallback for tiny 8×8 / 16×16 micro-icons.*

2. ⛔ **ZERO PIXELCRAFT LIBRARY RECONNAISSANCE:**
   * **DO NOT** browse `pixelcraft/` source files or `examples/` trying to learn the API.
   * **ALL APIs, imports, palettes, and rules are 100% self-contained in this document.**
   * Immediately write the generation script in **ONE tool call**. Do not waste the user's time or tokens!
   * *(Note: Filesystem tools like dir/search are fully permitted when integrating sprites into a game project, locating assets folders, or organizing assets in Godot/Unity).*

3. 🎯 **STRICT SCOPE DISCIPLINE (CREATE ONLY WHAT WAS ASKED):**
   * If the user asks for a **sprite** (e.g., "создай спрайт шлепы"):
     * Generate **ONLY ONE static sprite** (`output/<name>.png`).
     * **DO NOT** generate animations, GIFs, spritesheets, JSON metadata, or extra unrequested variants!
   * If the user asks for an **animation** or **spritesheet**:
     * Generate `output/<name>.gif` and/or `output/<name>_sheet.png`.
   * **NO ROOT CLUTTER:** Save the generation script in `output/generate_<name>.py` (never in project root).

---

## 🚀 COMPLETE API CHEAT SHEET (Procedural First)

```python
from pixelcraft import (
    Canvas,             # 2D pixel canvas
    Palette,            # Curated palettes & ramps
    Animation,          # Animation timeline
    print_ansi,         # Print TrueColor sprite directly in console
    save_png,           # save_png(canvas, "output/name.png", scale=1, preview_scale=8)
    save_gif,           # save_gif(anim, "output/name.gif", preview_scale=8)
    save_spritesheet,   # save_spritesheet(anim, "output/name.png", save_meta_json=True)
    lint_sprite,        # lint_sprite(canvas).summary() -> check orphan pixels/symmetry
)

# 1. Palettes & Ramps
palette = Palette.load("edg32")   # 'pico8' (16c), 'db16' (16c), 'sweetie16' (16c), 'db32' (32c), 'edg32' (32c)
ramp = Palette.create_ramp("#38b764", steps=4, hue_shift_deg=15)  # Dark shadow -> light highlight

# 2. Procedural Canvas Construction (The Golden Standard)
c = Canvas(width=24, height=24, palette=palette)

# --- Procedural Primitives ---
# 3D Shaded Sphere (heads, bodies, orbs, gems, eyes):
c.draw_shaded_sphere(cx=12, cy=12, radius=8, ramp=ramp, light_dir=(-0.6, -0.6))

# Shaded Cylinder (blades, pillars, armor limbs):
c.draw_shaded_cylinder(x=8, y=4, w=8, h=16, ramp=ramp, orientation="vertical")

# Scanline-Rasterized Polygons (horns, wings, shields, cloaks, ears):
c.draw_polygon([(12, 4), (4, 10), (8, 16)], fill_color=ramp[1], outline_color="#140c1c")

# Thick Lines (limbs, tentacles, heavy weapons):
c.draw_thick_line(x0=6, y0=16, x1=6, y1=22, thickness=2, color=ramp[0])

# Basic Primitives:
c.draw_rect(x=10, y=10, w=4, h=4, color="#ffffff", fill=True)
c.draw_circle(cx=12, cy=12, radius=3, color="#ff0000", fill=True)
c.draw_ellipse(cx=12, cy=12, rx=5, ry=3, color="#00ff00", fill=True)
c.draw_line(x0=2, y0=2, x1=22, y1=22, color="#ffffff")

# 3. Procedural Symmetry (Draw Left Side -> Mirror to Right!)
# Draw everything on the left half [0 .. width//2], then call:
c.mirror_horizontal(from_side="left")  # Guarantees 100% mathematical symmetry!

# 4. Filters & Polish
c = c.auto_outline("#140c1c")     # 1px crisp retro border
c = c.auto_shadow(dx=1, dy=1)     # Drop shadow
c = c.palette_swap({"#old": "#new"}) # Instant element variant reskin

# 5. Modifying Existing PNG
c = Canvas.from_png("output/existing.png")
```

---

## 🎨 Recommended Procedural Patterns

### Pattern 1: Procedural Character / Monster / Animal (Floppa, Goblin, Mech)
```python
from pixelcraft import Canvas, Palette, print_ansi, save_png, lint_sprite

palette = Palette.load("edg32")
body_ramp = Palette.create_ramp("#d77643", steps=5, hue_shift_deg=10) # Fur / skin
ear_ramp = Palette.create_ramp("#181425", steps=3)

c = Canvas(24, 24, palette=palette)

# Step 1: Draw Left Half of the Head & Features
c.draw_shaded_sphere(cx=11, cy=13, radius=8, ramp=body_ramp)

# Left Ear / Tuft (Polygon)
c.draw_polygon([(7, 8), (4, 1), (3, 0), (6, 5), (10, 8)], fill_color=ear_ramp[0], outline_color="#181425")

# Left Eye & Muzzle
c.draw_rect(x=6, y=11, w=3, h=3, color="#63c74d")  # Green eye
c.draw_pixel(7, 12, "#181425")                     # Pupil
c.draw_pixel(6, 11, "#ffffff")                     # Eye gleam
c.draw_rect(x=8, y=14, w=4, h=4, color="#ead4aa")  # Muzzle

# Step 2: Mirror Horizontally for Perfect Bilateral Symmetry!
c.mirror_horizontal(from_side="left")

# Step 3: Draw Center Details (Nose, Mouth)
c.draw_pixel(11, 14, "#f6757a") # Center nose
c.draw_pixel(12, 14, "#f6757a")

# Step 4: Crisp Dark Outline
c = c.auto_outline("#181425")

# Step 5: Save & Inspect
save_png(c, "output/character.png", scale=1, preview_scale=8)
```

---

## ⚡ 1-Step Execution Protocol

When user asks to create a sprite:
1. Write `output/generate_<name>.py` using **Procedural Geometric Primitives**.
2. Run `python output/generate_<name>.py`.
3. Inspect `output/<name>_preview.png` via `view_file` to confirm visual quality.
4. Present the result to the user with a markdown link to the image. Done!
