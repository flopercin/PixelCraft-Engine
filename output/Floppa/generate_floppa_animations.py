"""
Generate Complete Big Floppa Animation Suite for user in output/Floppa/
Animations:
1. floppa_ears_no_blink.gif & spritesheet (машет ушками и НЕ моргает)
2. floppa_ears_and_blink.gif & spritesheet (машет ушками И моргает)
3. floppa_fall.gif & spritesheet (анимация падения)
"""

import os
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

TARGET_DIR = r"C:\Users\flopercin\Documents\FloprSprites\output\Floppa"
os.makedirs(TARGET_DIR, exist_ok=True)

palette = Palette.load("edg32")

caracal_ramp = Palette.create_ramp("#c87830", steps=5, darken_factor=0.6, brighten_factor=0.45, hue_shift_deg=10)
cream_ramp = Palette.create_ramp("#f6eedf", steps=4, darken_factor=0.75, brighten_factor=0.25, hue_shift_deg=5)
eye_ramp = Palette.create_ramp("#529a36", steps=3, darken_factor=0.6, brighten_factor=0.5, hue_shift_deg=15)
nose_ramp = Palette.create_ramp("#d46b7a", steps=3, darken_factor=0.6, brighten_factor=0.35, hue_shift_deg=-10)

OUTLINE = "#120a12"
EAR_DARK = "#221420"
MARKING = "#20141e"
MOUTH_LINE = "#160a16"
WHITE = "#ffffff"
TONGUE = "#eb7488"
MOUTH_BG = "#2a101c"
WIND_COLOR = "#c8dff7"


def render_floppa_frame(
    ear_mode="neutral",
    eye_mode="open",
    mouth_mode="open_smile",
    paws_mode="loaf",
    wind_frame=0,
    body_offset_y=0
):
    canvas = Canvas(32, 32, palette=palette)

    if ear_mode == "neutral":
        canvas.draw_polygon([(3, 14), (5, 4), (12, 8), (11, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(28, 14), (26, 4), (19, 8), (20, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(6, 13), (6, 6), (11, 9), (10, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_polygon([(25, 13), (25, 6), (20, 9), (21, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(5, 4, 3, 1, thickness=2, color=OUTLINE)
        canvas.draw_line(3, 1, 2, 0, color=OUTLINE)
        canvas.draw_pixel(1, 0, color=OUTLINE)
        canvas.draw_thick_line(26, 4, 28, 1, thickness=2, color=OUTLINE)
        canvas.draw_line(28, 1, 29, 0, color=OUTLINE)
        canvas.draw_pixel(30, 0, color=OUTLINE)

    elif ear_mode == "flap_left":
        canvas.draw_polygon([(3, 14), (3, 6), (12, 9), (11, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(5, 13), (5, 8), (11, 10), (10, 14)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(3, 6, 1, 5, thickness=2, color=OUTLINE)
        canvas.draw_line(1, 5, 0, 4, color=OUTLINE)
        canvas.draw_pixel(0, 3, color=OUTLINE)

        canvas.draw_polygon([(28, 14), (26, 4), (19, 8), (20, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(25, 13), (25, 6), (20, 9), (21, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(26, 4, 28, 1, thickness=2, color=OUTLINE)
        canvas.draw_line(28, 1, 29, 0, color=OUTLINE)
        canvas.draw_pixel(30, 0, color=OUTLINE)

    elif ear_mode == "flap_right":
        canvas.draw_polygon([(3, 14), (5, 4), (12, 8), (11, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(6, 13), (6, 6), (11, 9), (10, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(5, 4, 3, 1, thickness=2, color=OUTLINE)
        canvas.draw_line(3, 1, 2, 0, color=OUTLINE)
        canvas.draw_pixel(1, 0, color=OUTLINE)

        canvas.draw_polygon([(28, 14), (28, 6), (19, 9), (20, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(26, 13), (26, 8), (20, 10), (21, 14)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(28, 6, 30, 5, thickness=2, color=OUTLINE)
        canvas.draw_line(30, 5, 31, 4, color=OUTLINE)
        canvas.draw_pixel(31, 3, color=OUTLINE)

    elif ear_mode == "flap_both":
        canvas.draw_polygon([(3, 14), (3, 6), (12, 9), (11, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(5, 13), (5, 8), (11, 10), (10, 14)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(3, 6, 1, 5, thickness=2, color=OUTLINE)
        canvas.draw_line(1, 5, 0, 4, color=OUTLINE)
        canvas.draw_pixel(0, 3, color=OUTLINE)

        canvas.draw_polygon([(28, 14), (28, 6), (19, 9), (20, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(26, 13), (26, 8), (20, 10), (21, 14)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(28, 6, 30, 5, thickness=2, color=OUTLINE)
        canvas.draw_line(30, 5, 31, 4, color=OUTLINE)
        canvas.draw_pixel(31, 3, color=OUTLINE)

    elif ear_mode == "fall_1":
        canvas.draw_polygon([(4, 14), (6, 3), (12, 7), (11, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(27, 14), (25, 3), (19, 7), (20, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(7, 13), (7, 5), (11, 8), (10, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_polygon([(24, 13), (24, 5), (20, 8), (21, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(6, 3, 5, 0, thickness=2, color=OUTLINE)
        canvas.draw_line(5, 0, 4, 0, color=OUTLINE)
        canvas.draw_thick_line(25, 3, 26, 0, thickness=2, color=OUTLINE)
        canvas.draw_line(26, 0, 27, 0, color=OUTLINE)

    elif ear_mode == "fall_2":
        canvas.draw_polygon([(3, 14), (5, 2), (12, 7), (11, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(27, 14), (24, 4), (19, 8), (20, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(6, 13), (6, 4), (11, 8), (10, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_polygon([(24, 13), (23, 6), (20, 9), (21, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(5, 2, 3, 0, thickness=2, color=OUTLINE)
        canvas.draw_pixel(2, 0, OUTLINE)
        canvas.draw_thick_line(24, 4, 23, 1, thickness=2, color=OUTLINE)
        canvas.draw_line(23, 1, 22, 0, color=OUTLINE)

    elif ear_mode == "fall_3":
        canvas.draw_polygon([(4, 14), (7, 4), (12, 8), (11, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(28, 14), (26, 2), (19, 7), (20, 14)], fill_color=EAR_DARK, outline_color=OUTLINE)
        canvas.draw_polygon([(7, 13), (8, 6), (11, 9), (10, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_polygon([(25, 13), (25, 4), (20, 8), (21, 13)], fill_color=cream_ramp[2], outline_color=None)
        canvas.draw_thick_line(7, 4, 8, 1, thickness=2, color=OUTLINE)
        canvas.draw_line(8, 1, 9, 0, color=OUTLINE)
        canvas.draw_thick_line(26, 2, 28, 0, thickness=2, color=OUTLINE)
        canvas.draw_pixel(29, 0, OUTLINE)

    cy_head = 17 + body_offset_y
    canvas.draw_shaded_sphere(cx=15, cy=cy_head, radius=11, ramp=caracal_ramp, light_dir=(-0.6, -0.6))
    canvas.draw_shaded_sphere(cx=10, cy=cy_head + 2, radius=6, ramp=caracal_ramp, light_dir=(-0.6, -0.6))
    canvas.draw_shaded_sphere(cx=21, cy=cy_head + 2, radius=6, ramp=caracal_ramp, light_dir=(-0.6, -0.6))

    canvas.draw_line(12, 9 + body_offset_y, 12, 12 + body_offset_y, color=MARKING)
    canvas.draw_line(19, 9 + body_offset_y, 19, 12 + body_offset_y, color=MARKING)

    ey = 13 + body_offset_y
    if eye_mode == "open":
        canvas.draw_rect(8, ey, 5, 4, color=OUTLINE)
        canvas.draw_rect(19, ey, 5, 4, color=OUTLINE)
        canvas.draw_pixel(8, ey, caracal_ramp[2])
        canvas.draw_pixel(12, ey, caracal_ramp[2])
        canvas.draw_pixel(8, ey + 3, caracal_ramp[2])
        canvas.draw_pixel(12, ey + 3, caracal_ramp[1])
        canvas.draw_pixel(19, ey, caracal_ramp[1])
        canvas.draw_pixel(23, ey, caracal_ramp[0])
        canvas.draw_pixel(19, ey + 3, caracal_ramp[1])
        canvas.draw_pixel(23, ey + 3, caracal_ramp[0])

        canvas.draw_rect(9, ey + 1, 3, 2, color=eye_ramp[1])
        canvas.draw_rect(20, ey + 1, 3, 2, color=eye_ramp[1])
        canvas.draw_pixel(10, ey + 1, OUTLINE)
        canvas.draw_pixel(10, ey + 2, OUTLINE)
        canvas.draw_pixel(21, ey + 1, OUTLINE)
        canvas.draw_pixel(21, ey + 2, OUTLINE)
        canvas.draw_pixel(9, ey + 1, WHITE)
        canvas.draw_pixel(20, ey + 1, WHITE)

    elif eye_mode == "blink":
        canvas.draw_line(8, ey + 1, 12, ey + 1, color=caracal_ramp[3])
        canvas.draw_line(19, ey + 1, 23, ey + 1, color=caracal_ramp[2])
        canvas.draw_pixel(8, ey + 2, OUTLINE)
        canvas.draw_pixel(9, ey + 3, OUTLINE)
        canvas.draw_pixel(10, ey + 3, OUTLINE)
        canvas.draw_pixel(11, ey + 3, OUTLINE)
        canvas.draw_pixel(12, ey + 2, OUTLINE)

        canvas.draw_pixel(19, ey + 2, OUTLINE)
        canvas.draw_pixel(20, ey + 3, OUTLINE)
        canvas.draw_pixel(21, ey + 3, OUTLINE)
        canvas.draw_pixel(22, ey + 3, OUTLINE)
        canvas.draw_pixel(23, ey + 2, OUTLINE)

    elif eye_mode == "wide_fall":
        canvas.draw_rect(7, ey - 1, 6, 6, color=OUTLINE)
        canvas.draw_rect(18, ey - 1, 6, 6, color=OUTLINE)
        canvas.draw_rect(8, ey, 4, 4, color=WHITE)
        canvas.draw_rect(19, ey, 4, 4, color=WHITE)
        canvas.draw_rect(9, ey + 1, 3, 3, color=eye_ramp[1])
        canvas.draw_rect(20, ey + 1, 3, 3, color=eye_ramp[1])
        canvas.draw_rect(10, ey + 2, 2, 2, color=OUTLINE)
        canvas.draw_rect(21, ey + 2, 2, 2, color=OUTLINE)
        canvas.draw_pixel(9, ey + 1, WHITE)
        canvas.draw_pixel(20, ey + 1, WHITE)

    canvas.draw_line(12, ey + 2, 13, ey + 5, color=MARKING)
    canvas.draw_line(19, ey + 2, 18, ey + 5, color=MARKING)

    cy_chin = 25 + body_offset_y
    canvas.draw_shaded_sphere(cx=15, cy=cy_chin, radius=3, ramp=cream_ramp, light_dir=(-0.5, -0.5))
    canvas.draw_line(13, cy_chin + 1, 18, cy_chin + 1, color=cream_ramp[1])
    canvas.draw_line(14, cy_chin + 2, 17, cy_chin + 2, color=cream_ramp[0])

    cy_pads = 21 + body_offset_y
    canvas.draw_shaded_sphere(cx=11, cy=cy_pads, radius=4, ramp=cream_ramp, light_dir=(-0.5, -0.5))
    canvas.draw_shaded_sphere(cx=20, cy=cy_pads, radius=4, ramp=cream_ramp, light_dir=(-0.5, -0.5))

    canvas.draw_pixel(9, cy_pads, MARKING)
    canvas.draw_pixel(10, cy_pads + 1, MARKING)
    canvas.draw_pixel(21, cy_pads + 1, MARKING)
    canvas.draw_pixel(22, cy_pads, MARKING)

    ny = 18 + body_offset_y
    canvas.draw_polygon([(14, ny), (17, ny), (16, ny + 2), (15, ny + 2)], fill_color=nose_ramp[1], outline_color=OUTLINE)
    canvas.draw_pixel(15, ny, nose_ramp[2])
    canvas.draw_pixel(16, ny, nose_ramp[2])
    canvas.draw_pixel(15, ny + 1, OUTLINE)
    canvas.draw_pixel(16, ny + 1, OUTLINE)

    my = 21 + body_offset_y
    if mouth_mode == "open_smile":
        canvas.draw_line(15, my, 16, my, color=MOUTH_LINE)
        canvas.draw_pixel(14, my + 1, MOUTH_LINE)
        canvas.draw_pixel(13, my + 1, MOUTH_LINE)
        canvas.draw_pixel(12, my, MOUTH_LINE)
        canvas.draw_pixel(17, my + 1, MOUTH_LINE)
        canvas.draw_pixel(18, my + 1, MOUTH_LINE)
        canvas.draw_pixel(19, my, MOUTH_LINE)

        canvas.draw_rect(14, my + 2, 4, 2, color=MOUTH_BG)
        canvas.draw_rect(15, my + 2, 2, 2, color=TONGUE)
        canvas.draw_pixel(14, my + 3, TONGUE)
        canvas.draw_pixel(17, my + 3, TONGUE)

        canvas.draw_line(14, my + 4, 17, my + 4, color=MOUTH_LINE)
        canvas.draw_pixel(13, my + 3, MOUTH_LINE)
        canvas.draw_pixel(18, my + 3, MOUTH_LINE)

    elif mouth_mode == "classic_3":
        canvas.draw_line(15, my, 16, my, color=MOUTH_LINE)
        canvas.draw_pixel(14, my + 1, MOUTH_LINE)
        canvas.draw_pixel(13, my + 2, MOUTH_LINE)
        canvas.draw_pixel(12, my + 2, MOUTH_LINE)
        canvas.draw_pixel(11, my + 1, MOUTH_LINE)

        canvas.draw_pixel(17, my + 1, MOUTH_LINE)
        canvas.draw_pixel(18, my + 2, MOUTH_LINE)
        canvas.draw_pixel(19, my + 2, MOUTH_LINE)
        canvas.draw_pixel(20, my + 1, MOUTH_LINE)
        canvas.draw_line(14, my + 3, 17, my + 3, color=cream_ramp[1])

    elif mouth_mode == "fall_o":
        canvas.draw_line(15, my, 16, my, color=MOUTH_LINE)
        canvas.draw_rect(14, my + 1, 4, 4, color=OUTLINE)
        canvas.draw_rect(15, my + 2, 2, 2, color=MOUTH_BG)
        canvas.draw_pixel(15, my + 3, TONGUE)
        canvas.draw_pixel(16, my + 3, TONGUE)

    if paws_mode == "fall_spread":
        canvas.draw_thick_line(6, 21, 2, 19, thickness=2, color=caracal_ramp[3])
        canvas.draw_rect(0, 18, 3, 3, color=cream_ramp[3])
        canvas.draw_pixel(0, 18, OUTLINE)
        canvas.draw_pixel(1, 17, OUTLINE)

        canvas.draw_thick_line(25, 21, 29, 19, thickness=2, color=caracal_ramp[1])
        canvas.draw_rect(29, 18, 3, 3, color=cream_ramp[2])
        canvas.draw_pixel(31, 18, OUTLINE)
        canvas.draw_pixel(30, 17, OUTLINE)

        canvas.draw_rect(4, 27, 4, 3, color=caracal_ramp[2])
        canvas.draw_rect(23, 27, 4, 3, color=caracal_ramp[0])

    canvas = canvas.auto_outline(OUTLINE)

    wy = 20 + body_offset_y
    if paws_mode == "fall_spread":
        canvas.draw_line(7, wy, 1, wy - 3, color=WHITE)
        canvas.draw_line(6, wy + 2, 0, wy - 1, color=WHITE)
        canvas.draw_line(24, wy, 30, wy - 3, color=WHITE)
        canvas.draw_line(25, wy + 2, 31, wy - 1, color=WHITE)
    else:
        canvas.draw_line(7, wy, 1, wy - 1, color=WHITE)
        canvas.draw_line(6, wy + 2, 0, wy + 2, color=WHITE)
        canvas.draw_line(7, wy + 3, 2, wy + 5, color=WHITE)

        canvas.draw_line(24, wy, 30, wy - 1, color=WHITE)
        canvas.draw_line(25, wy + 2, 31, wy + 2, color=WHITE)
        canvas.draw_line(24, wy + 3, 29, wy + 5, color=WHITE)

    if wind_frame == 1:
        canvas.draw_line(3, 31, 3, 24, color=WIND_COLOR)
        canvas.draw_line(28, 29, 28, 22, color=WIND_COLOR)
        canvas.draw_line(15, 31, 15, 29, color=WIND_COLOR)
    elif wind_frame == 2:
        canvas.draw_line(2, 28, 2, 21, color=WIND_COLOR)
        canvas.draw_line(29, 31, 29, 24, color=WIND_COLOR)
        canvas.draw_line(6, 31, 6, 26, color=WIND_COLOR)
        canvas.draw_line(25, 30, 25, 25, color=WIND_COLOR)
    elif wind_frame == 3:
        canvas.draw_line(4, 30, 4, 23, color=WIND_COLOR)
        canvas.draw_line(27, 30, 27, 23, color=WIND_COLOR)
        canvas.draw_line(16, 31, 16, 29, color=WIND_COLOR)

    return canvas


print("Rendering animation frames...")

anim_no_blink = Animation(name="floppa_ears_no_blink", default_duration_ms=200)

f_rest = render_floppa_frame(ear_mode="neutral", eye_mode="open", mouth_mode="open_smile")
f_flop_l = render_floppa_frame(ear_mode="flap_left", eye_mode="open", mouth_mode="open_smile")
f_flop_r = render_floppa_frame(ear_mode="flap_right", eye_mode="open", mouth_mode="open_smile")
f_flop_both = render_floppa_frame(ear_mode="flap_both", eye_mode="open", mouth_mode="open_smile")

anim_no_blink.add_frame(f_rest, duration_ms=450)
anim_no_blink.add_frame(f_flop_l, duration_ms=180)
anim_no_blink.add_frame(f_rest, duration_ms=200)
anim_no_blink.add_frame(f_flop_r, duration_ms=180)
anim_no_blink.add_frame(f_rest, duration_ms=200)
anim_no_blink.add_frame(f_flop_both, duration_ms=220)
anim_no_blink.add_frame(f_rest, duration_ms=350)

gif1_path = os.path.join(TARGET_DIR, "floppa_ears_no_blink.gif")
sheet1_path = os.path.join(TARGET_DIR, "floppa_ears_no_blink_sheet.png")
save_gif(anim_no_blink, gif1_path, scale=1, preview_scale=8, loop=0)
save_spritesheet(anim_no_blink, sheet1_path, scale=1, layout="horizontal", save_meta_json=True)
save_spritesheet(anim_no_blink, os.path.join(TARGET_DIR, "floppa_ears_no_blink_sheet_preview.png"), scale=4, layout="horizontal", save_meta_json=False)

print("Animation 1 (Ears, No Blink) saved to output/Floppa!")

anim_and_blink = Animation(name="floppa_ears_and_blink", default_duration_ms=200)

f_blink = render_floppa_frame(ear_mode="neutral", eye_mode="blink", mouth_mode="open_smile")

anim_and_blink.add_frame(f_rest, duration_ms=500)
anim_and_blink.add_frame(f_flop_l, duration_ms=180)
anim_and_blink.add_frame(f_rest, duration_ms=200)
anim_and_blink.add_frame(f_flop_r, duration_ms=180)
anim_and_blink.add_frame(f_rest, duration_ms=220)
anim_and_blink.add_frame(f_flop_both, duration_ms=200)
anim_and_blink.add_frame(f_blink, duration_ms=280)
anim_and_blink.add_frame(f_rest, duration_ms=400)

gif2_path = os.path.join(TARGET_DIR, "floppa_ears_and_blink.gif")
sheet2_path = os.path.join(TARGET_DIR, "floppa_ears_and_blink_sheet.png")
save_gif(anim_and_blink, gif2_path, scale=1, preview_scale=8, loop=0)
save_spritesheet(anim_and_blink, sheet2_path, scale=1, layout="horizontal", save_meta_json=True)
save_spritesheet(anim_and_blink, os.path.join(TARGET_DIR, "floppa_ears_and_blink_sheet_preview.png"), scale=4, layout="horizontal", save_meta_json=False)

print("Animation 2 (Ears & Blink) saved to output/Floppa!")

anim_fall = Animation(name="floppa_fall", default_duration_ms=130)

f_fall_1 = render_floppa_frame(
    ear_mode="fall_1", eye_mode="wide_fall", mouth_mode="fall_o", paws_mode="fall_spread",
    wind_frame=1, body_offset_y=0
)
f_fall_2 = render_floppa_frame(
    ear_mode="fall_2", eye_mode="wide_fall", mouth_mode="fall_o", paws_mode="fall_spread",
    wind_frame=2, body_offset_y=1
)
f_fall_3 = render_floppa_frame(
    ear_mode="fall_1", eye_mode="wide_fall", mouth_mode="fall_o", paws_mode="fall_spread",
    wind_frame=3, body_offset_y=0
)
f_fall_4 = render_floppa_frame(
    ear_mode="fall_3", eye_mode="wide_fall", mouth_mode="fall_o", paws_mode="fall_spread",
    wind_frame=2, body_offset_y=-1
)

anim_fall.add_frame(f_fall_1, duration_ms=130)
anim_fall.add_frame(f_fall_2, duration_ms=130)
anim_fall.add_frame(f_fall_3, duration_ms=130)
anim_fall.add_frame(f_fall_4, duration_ms=130)

gif3_path = os.path.join(TARGET_DIR, "floppa_fall.gif")
sheet3_path = os.path.join(TARGET_DIR, "floppa_fall_sheet.png")
save_gif(anim_fall, gif3_path, scale=1, preview_scale=8, loop=0)
save_spritesheet(anim_fall, sheet3_path, scale=1, layout="horizontal", save_meta_json=True)
save_spritesheet(anim_fall, os.path.join(TARGET_DIR, "floppa_fall_sheet_preview.png"), scale=4, layout="horizontal", save_meta_json=False)

print("Animation 3 (Fall) saved to output/Floppa!")
print("All 3 requested animations generated successfully!")
