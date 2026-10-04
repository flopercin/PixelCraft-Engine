"""
Generate a consolidated HTML Gallery showing all 4 refined sprites with zoom controls.
"""

from pathlib import Path

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>PixelCraft Sprites Showcase</title>
<style>
  body {
    margin: 0;
    padding: 30px;
    background: #141020;
    color: #e4e6eb;
    font-family: system-ui, -apple-system, sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  h1 { margin-bottom: 6px; color: #5bc0be; font-size: 1.6rem; }
  p { margin-top: 0; margin-bottom: 24px; color: #8e9aaf; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 24px;
    max-width: 1100px;
    width: 100%;
  }
  .card {
    background: #1d1733;
    border: 2px solid #2d244c;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }
  .card h3 {
    margin: 0 0 14px 0;
    font-size: 1.1rem;
    color: #ffd166;
  }
  .viewport {
    background-color: #241c38;
    background-image: linear-gradient(45deg, #1b152d 25%, transparent 25%),
      linear-gradient(-45deg, #1b152d 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, #1b152d 75%),
      linear-gradient(-45deg, transparent 75%, #1b152d 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0px;
    padding: 24px;
    border-radius: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 160px;
  }
  .pixelated {
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    transform: scale(6);
    transform-origin: center;
  }
  .desc {
    margin-top: 24px;
    font-size: 0.85rem;
    color: #a5a5b5;
    text-align: center;
    line-height: 1.4;
  }
</style>
</head>
<body>
  <h1>PixelCraft Sprite Showcase</h1>
  <p>Iconic, readable retro sprites created via programmatic ASCII token-grid matrices</p>

  <div class="grid">
    <div class="card">
      <h3>1. Health Potion</h3>
      <div class="viewport">
        <img class="pixelated" src="potion.png" alt="Health Potion" />
      </div>
      <div class="desc">
        16x16 flask with cork stopper, glass highlight rim, and crimson liquid.
      </div>
    </div>

    <div class="card">
      <h3>2. Chibi Knight</h3>
      <div class="viewport">
        <img class="pixelated" src="knight.png" alt="Chibi Knight" />
      </div>
      <div class="desc">
        16x16 steel helmet with glowing visor, red plume, gold shield, sword, and boots.
      </div>
    </div>

    <div class="card">
      <h3>3. Animated Slime</h3>
      <div class="viewport">
        <img class="pixelated" src="slime_idle.gif" alt="Animated Slime" />
      </div>
      <div class="desc">
        16x16 teardrop dome with jelly shine, cute eyes, blush, and 4-frame squish & blink loop.
      </div>
    </div>

    <div class="card">
      <h3>4. Straight Broadsword</h3>
      <div class="viewport">
        <img class="pixelated" src="elemental_sword.png" alt="Broadsword" />
      </div>
      <div class="desc">
        20x20 perfectly vertical razor blade, golden winged crossguard, ruby, and grip.
      </div>
    </div>

    <div class="card">
      <h3>5. Mana Potion (Edited)</h3>
      <div class="viewport">
        <img class="pixelated" src="mana_potion.png" alt="Mana Potion" />
      </div>
      <div class="desc">
        Loaded from Health Potion PNG and transformed via <code>palette_swap()</code>.
      </div>
    </div>

    <div class="card">
      <h3>6. King Knight (Edited)</h3>
      <div class="viewport">
        <img class="pixelated" src="king_knight.png" alt="King Knight" />
      </div>
      <div class="desc">
        Loaded from Knight PNG, reskinned to gold armor + royal purple with a golden crown.
      </div>
    </div>

    <div class="card">
      <h3>7. Void Boss (32x32 Procedural)</h3>
      <div class="viewport">
        <img class="pixelated" style="transform: scale(3.5);" src="void_boss_32x32.png" alt="Void Boss" />
      </div>
      <div class="desc">
        100% procedural 32x32 sprite (ZERO ASCII lines) using 3D spherical normal shading, polygons, and ramps.
      </div>
    </div>
  </div>
</body>
</html>
"""

Path("output/gallery.html").write_text(html, encoding="utf-8")
print("Gallery written to output/gallery.html")
