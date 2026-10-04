"""
Example 6: Complex 32x32 Boss Monster (100% Procedural - ZERO ASCII Grids)
Demonstrates:
- Creating large, complex 32x32 sprites WITHOUT any ASCII strings
- 3D Spherical normal shading (draw_shaded_sphere)
- Polygon rasterization for horns/wings/fins (draw_polygon)
- Thick geometric limbs/tentacles (draw_thick_line)
- Multiple coordinated color ramps (flesh, magic crystals, gold armor plates)
- Drop shadow and auto-outline
"""

import math
from pixelcraft import Canvas, Palette, print_ansi, save_png, lint_sprite

palette = Palette.load("edg32")

void_ramp = Palette.create_ramp("#68386c", steps=5, darken_factor=0.6, brighten_factor=0.5, hue_shift_deg=-15)
fire_ramp = Palette.create_ramp("#f77622", steps=4, darken_factor=0.7, brighten_factor=0.6, hue_shift_deg=30)
gold_ramp = Palette.create_ramp("#e4a672", steps=4, darken_factor=0.5, brighten_factor=0.4, hue_shift_deg=10)
cyan_ramp = Palette.create_ramp("#2ce8f5", steps=4, darken_factor=0.6, brighten_factor=0.4, hue_shift_deg=20)

boss = Canvas(32, 32, palette=palette)

boss.draw_polygon([(11, 10), (3, 4), (2, 2), (7, 6), (13, 11)], fill_color=gold_ramp[1], outline_color="#181425")
boss.draw_polygon([(20, 10), (28, 4), (29, 2), (24, 6), (18, 11)], fill_color=gold_ramp[1], outline_color="#181425")

boss.draw_thick_line(11, 23, 7, 28, thickness=2, color=void_ramp[1])
boss.draw_thick_line(7, 28, 5, 30, thickness=1, color=void_ramp[0])

boss.draw_thick_line(20, 23, 24, 28, thickness=2, color=void_ramp[1])
boss.draw_thick_line(24, 28, 26, 30, thickness=1, color=void_ramp[0])

boss.draw_thick_line(15, 24, 15, 29, thickness=2, color=void_ramp[1])
boss.draw_pixel(15, 30, void_ramp[0])

boss.draw_shaded_sphere(cx=15, cy=16, radius=9, ramp=void_ramp, light_dir=(-0.6, -0.6))

boss.draw_shaded_sphere(cx=14, cy=16, radius=4, ramp=fire_ramp, light_dir=(-0.6, -0.6))
boss.draw_line(14, 14, 14, 18, color="#181425")
boss.draw_pixel(13, 16, color="#181425")
boss.draw_pixel(15, 16, color="#181425")
boss.draw_pixel(12, 13, color="#ffffff")
boss.draw_pixel(13, 13, color="#ffffff")

boss.draw_shaded_sphere(cx=26, cy=9, radius=3, ramp=cyan_ramp, light_dir=(-0.6, -0.6))
boss.draw_pixel(25, 8, color="#ffffff")

boss.draw_shaded_sphere(cx=5, cy=20, radius=2, ramp=cyan_ramp, light_dir=(-0.6, -0.6))
boss.draw_pixel(4, 19, color="#ffffff")

boss = boss.auto_outline("#181425")

print_ansi(boss, title="32x32 Void Beholder Boss (Procedural)")
save_png(boss, "output/void_boss_32x32.png", scale=1, preview_scale=8)

rep = lint_sprite(boss)
print(rep.summary())
