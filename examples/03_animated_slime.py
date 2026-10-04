"""
Refined Example 3: Classic Animated Slime (16x16)
Focus: Iconic teardrop/dome silhouette, shiny specular highlight, expressive centered eyes,
squish & stretch idle bounce, and happy blink animation.
"""

from pixelcraft import (
    Canvas,
    Palette,
    Animation,
    print_ansi,
    save_png,
    save_gif,
    save_spritesheet,
    lint_sprite,
)

palette = Palette({
    ".": None,
    "#": "#140c1c",
    "L": "#a7f070",
    "G": "#38b764",
    "D": "#257179",
    "B": "#29366f",
    "W": "#ffffff",
    "E": "#0f380f",
    "P": "#ff77a8",
})

slime_base_ascii = """
................
.......##.......
......#LL#......
.....#LLLL#.....
....#LWWLLLL#...
...#LLWWLLGGG#..
..#LLLLGGGGGGG#.
..#LL#W##W#GGG#.
..#LL#E##E#GGG#.
..#LP######PGG#.
..#GGGGGGGGGGG#.
..#DDDDDDDDDDD#.
...#BBBBBBBBB#..
....#########...
................
................
"""

slime_base = Canvas.from_ascii(slime_base_ascii, palette)

slime_squish_ascii = """
................
................
................
......####......
.....#LLLL#.....
....#LWWLLLL#...
...#LLWWLLGGG#..
..#LLLLGGGGGGG#.
..#LL#W##W#GGG#.
..#LP#E##E#PGG#.
..#GG######GGG#.
.#DDDDDDDDDDDDD#
.###############
................
................
................
"""
slime_squish = Canvas.from_ascii(slime_squish_ascii, palette)

slime_blink_ascii = """
................
.......##.......
......#LL#......
.....#LLLL#.....
....#LWWLLLL#...
...#LLWWLLGGG#..
..#LLLLGGGGGGG#.
..#LL######GGG#.
..#LL#W##W#GGG#.
..#LP######PGG#.
..#GGGGGGGGGGG#.
..#DDDDDDDDDDD#.
...#BBBBBBBBB#..
....#########...
................
................
"""
slime_blink = Canvas.from_ascii(slime_blink_ascii, palette)

anim = Animation(name="slime_idle", default_duration_ms=160)
anim.add_frame(slime_base, duration_ms=220)
anim.add_frame(slime_squish, duration_ms=160)
anim.add_frame(slime_base, duration_ms=200)
anim.add_frame(slime_blink, duration_ms=140)

print_ansi(slime_base, title="Classic RPG Slime (16x16)")

save_gif(anim, "output/slime_idle.gif", scale=1, preview_scale=8, loop=0)
save_spritesheet(anim, "output/slime_sheet.png", scale=1, layout="horizontal", save_meta_json=True)
save_spritesheet(anim, "output/slime_sheet_preview.png", scale=4, layout="horizontal", save_meta_json=False)

print("Saved GIF and Spritesheet to output/")

rep = lint_sprite(slime_base)
print(rep.summary())
