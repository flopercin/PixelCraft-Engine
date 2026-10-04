"""
Refined Example 2: Classic Chibi Knight (16x16)
Focus: Iconic silhouette, readable proportions, clear negative space between limbs, shield and sword.
"""

from pixelcraft import Canvas, Palette, print_ansi, save_png, lint_sprite

palette = Palette({
    ".": None,
    "#": "#140c1c",
    "R": "#d04648",
    "r": "#ff77a8",
    "S": "#8595a1",
    "s": "#deeed6",
    "D": "#4e4a4e",
    "B": "#597dce",
    "G": "#dad45e",
    "g": "#d27d2c",
    "L": "#854c30",
    "W": "#ffffff",
})

knight_ascii = """
......#RR#......
.....#RRrr#.....
....#SSSSSS#....
...#SSssssSS#...
...#S######S#...
...#S#W##W#S#...
..##BBBBBBBB##..
.#GG#BBBBBB#s#..
.#GG#BBBBBB#s#..
.#gg#LLLLLL#S#..
..##S#DDDD#S##..
...#DD#..#DD#...
...#DD#..#DD#...
...#LL#..#LL#...
...####..####...
................
"""

knight = Canvas.from_ascii(knight_ascii, palette)

print_ansi(knight, title="Classic Chibi Knight (16x16)")
save_png(knight, "output/knight.png", scale=1, preview_scale=8)

rep = lint_sprite(knight)
print(rep.summary())
