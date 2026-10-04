"""
Refined Example 1: Classic RPG Health Potion (16x16)
Focus: Silhouette, readability, glass shine, liquid volume.
"""

from pixelcraft import Canvas, Palette, print_ansi, save_png, lint_sprite

palette = Palette({
    ".": None,
    "#": "#140c1c",
    "C": "#854c30",
    "c": "#d27d2c",
    "G": "#8595a1",
    "g": "#deeed6",
    "W": "#ffffff",
    "R": "#d04648",
    "r": "#ff77a8",
    "D": "#442434",
})

potion_ascii = """
................
......ccCC......
......CCCC......
.....#gggg#.....
.....#GGGG#.....
....#GWW..G#....
...#GWWrrrrr#...
..#GWWrrrrrrr#..
..#GWWRRRRRRR#..
..#GWWRRRRRRD#..
..#GWWRRRRRDD#..
...#GWRRRRDD#...
...#GDDDDDD#....
....#GGDDGG#....
.....######.....
................
"""

potion = Canvas.from_ascii(potion_ascii, palette)

print_ansi(potion, title="Classic Health Potion (16x16)")
save_png(potion, "output/potion.png", scale=1, preview_scale=8)

rep = lint_sprite(potion)
print(rep.summary())
