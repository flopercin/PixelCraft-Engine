"""
Example 5: Editing and Modifying Existing Sprites
Demonstrates:
1. Loading an existing PNG file into Canvas (Canvas.from_png)
2. Palette Swapping (Health Potion -> Blue Mana Potion)
3. Adding accessories / overlays (Golden Crown on Knight)
4. Deconstructing any sprite into an editable ASCII token matrix + Palette dictionary
"""

from pixelcraft import Canvas, Palette, print_ansi, save_png, lint_sprite

print("\n--- 1. Modifying Health Potion -> Mana Potion ---")
potion = Canvas.from_png("output/potion.png")

mana_potion = potion.palette_swap({
    "#d04648": "#29adff",
    "#ff77a8": "#73eff7",
    "#442434": "#1d2b53",
})

print_ansi(mana_potion, title="Mana Potion (Edited from Health Potion)")
save_png(mana_potion, "output/mana_potion.png", scale=1, preview_scale=8)

print("\n--- 2. Upgrading Knight -> Golden King Knight ---")
knight = Canvas.from_png("output/knight.png")

king_knight = knight.palette_swap({
    "#8595a1": "#edad54",
    "#deeed6": "#fee761",
    "#4e4a4e": "#d27d2c",
    "#597dce": "#7e2553",
})

king_knight.draw_pixel(5, 1, "#fee761")
king_knight.draw_pixel(7, 0, "#fee761")
king_knight.draw_pixel(9, 1, "#fee761")
king_knight.draw_pixel(7, 1, "#d04648")

print_ansi(king_knight, title="Golden King Knight (With Crown)")
save_png(king_knight, "output/king_knight.png", scale=1, preview_scale=8)

print("\n--- 3. Deconstructed ASCII Matrix of Mana Potion ---")
ascii_grid, pal_dict = mana_potion.to_ascii_definition()
print("Extracted Palette:")
for token, hex_val in pal_dict.items():
    print(f"  '{token}': '{hex_val}'")

print("\nEditable ASCII Grid (AI can copy, modify, and reload):")
print(ascii_grid)
