"""
pixelcraft.canvas
Core Canvas and LayeredCanvas classes providing ASCII grid parsing, symmetric generation,
pixel-perfect drawing primitives, dithering, and retro pixel-art transformations.
"""

from typing import Dict, List, Optional, Set, Tuple, Union
import textwrap
from copy import deepcopy
from pathlib import Path

from .palette import Palette, RGBA, ColorInput, parse_color, rgba_to_hex


class Canvas:
    """
    A 2D pixel canvas for procedural and grid-based pixel art generation.
    Pixels are stored in row-major order as (R, G, B, A) tuples or None (transparent).
    """

    def __init__(
        self,
        width: int,
        height: int,
        default_color: ColorInput = None,
        palette: Optional[Palette] = None,
    ):
        if width <= 0 or height <= 0:
            raise ValueError(f"Canvas dimensions must be positive integers, got {width}x{height}")
        self.width = width
        self.height = height
        self.palette = palette
        parsed_default = self.resolve_color(default_color)
        self.pixels: List[List[Optional[RGBA]]] = [
            [parsed_default for _ in range(width)] for _ in range(height)
        ]

    def resolve_color(self, color: ColorInput) -> Optional[RGBA]:
        """Resolves color against the canvas's palette if present, or parses standard hex/color names."""
        if color is None:
            return None
        if self.palette is not None and isinstance(color, str) and self.palette.has(color):
            return self.palette.get(color)
        return parse_color(color)


    @classmethod
    def from_ascii(
        cls,
        ascii_grid: str,
        palette: Union[Palette, Dict[str, ColorInput]],
        strict: bool = True,
    ) -> "Canvas":
        """
        Create a Canvas from a multi-line ASCII/string grid.
        Each character corresponds to a color in the palette. '.' and ' ' default to transparent.

        If strict=True: Raises ValueError with exact line numbers if lines have unequal lengths.
        If strict=False: Automatically pads shorter lines with transparent pixels.
        """
        if isinstance(palette, dict):
            palette = Palette(palette)

        raw_lines = ascii_grid.splitlines()
        while raw_lines and not raw_lines[0].strip():
            raw_lines.pop(0)
        while raw_lines and not raw_lines[-1].strip():
            raw_lines.pop()

        if not raw_lines:
            raise ValueError("ASCII grid is empty!")

        dedented = textwrap.dedent("\n".join(raw_lines)).splitlines()

        height = len(dedented)
        line_lengths = [len(line) for line in dedented]
        max_width = max(line_lengths)

        if strict and len(set(line_lengths)) > 1:
            mismatches = []
            for idx, line in enumerate(dedented):
                if len(line) != max_width:
                    mismatches.append(f"Line {idx + 1} (length {len(line)}, expected {max_width}): '{line}'")
            detail = "\n  ".join(mismatches[:5])
            raise ValueError(
                f"ASCII grid has inconsistent row lengths (expected {max_width}). Errors:\n  {detail}\n"
                f"Fix the row lengths to match exactly {max_width} characters, or set strict=False."
            )

        canvas = cls(width=max_width, height=height, palette=palette)
        for y, line in enumerate(dedented):
            for x in range(max_width):
                char = line[x] if x < len(line) else "."
                try:
                    canvas.pixels[y][x] = palette.get(char)
                except KeyError:
                    raise KeyError(
                        f"Unknown character '{char}' at grid coordinate (x={x}, y={y}, row {y+1}, col {x+1}). "
                        f"Available palette keys: {palette.keys()}"
                    )

        return canvas

    @classmethod
    def from_ascii_symmetric(
        cls,
        half_ascii_grid: str,
        palette: Union[Palette, Dict[str, ColorInput]],
        axis: str = "x",
        include_center: bool = False,
        strict: bool = True,
    ) -> "Canvas":
        """
        Construct a perfectly symmetrical sprite from half an ASCII grid.
        AI only needs to draw the LEFT half (axis='x') or TOP half (axis='y').

        axis='x': Horizontal symmetry (Left side mirrored to Right).
          - include_center=False: width becomes 2 * half_width (even width).
          - include_center=True: last column of half_grid is the center spine (odd width: 2 * half_width - 1).
        axis='y': Vertical symmetry (Top mirrored to Bottom).
        """
        if isinstance(palette, dict):
            palette = Palette(palette)

        half = cls.from_ascii(half_ascii_grid, palette=palette, strict=strict)

        if axis == "x":
            if include_center:
                full_w = half.width * 2 - 1
                full = cls(width=full_w, height=half.height, palette=palette)
                for y in range(half.height):
                    for x in range(half.width):
                        color = half.get_pixel(x, y)
                        full.set_pixel(x, y, color)
                        mirror_x = full_w - 1 - x
                        full.set_pixel(mirror_x, y, color)
            else:
                full_w = half.width * 2
                full = cls(width=full_w, height=half.height, palette=palette)
                for y in range(half.height):
                    for x in range(half.width):
                        color = half.get_pixel(x, y)
                        full.set_pixel(x, y, color)
                        mirror_x = full_w - 1 - x
                        full.set_pixel(mirror_x, y, color)
            return full

        elif axis == "y":
            if include_center:
                full_h = half.height * 2 - 1
                full = cls(width=half.width, height=full_h, palette=palette)
                for y in range(half.height):
                    for x in range(half.width):
                        color = half.get_pixel(x, y)
                        full.set_pixel(x, y, color)
                        mirror_y = full_h - 1 - y
                        full.set_pixel(x, mirror_y, color)
            else:
                full_h = half.height * 2
                full = cls(width=half.width, height=full_h, palette=palette)
                for y in range(half.height):
                    for x in range(half.width):
                        color = half.get_pixel(x, y)
                        full.set_pixel(x, y, color)
                        mirror_y = full_h - 1 - y
                        full.set_pixel(x, mirror_y, color)
            return full
        else:
            raise ValueError(f"Axis must be 'x' or 'y', got '{axis}'")

    @classmethod
    def from_png(cls, path: Union[str, Path]) -> "Canvas":
        """
        Load any existing PNG file into an editable Canvas.
        Automatically extracts the palette used in the image.
        """
        from PIL import Image
        img = Image.open(path).convert("RGBA")
        return cls.from_image(img)

    @classmethod
    def from_image(cls, img: "Image.Image") -> "Canvas":
        """Load from an existing PIL Image (RGBA)."""
        w, h = img.size
        canvas = cls(w, h)
        palette = Palette()
        unique_colors = set()

        for y in range(h):
            for x in range(w):
                r, g, b, a = img.getpixel((x, y))
                if a == 0:
                    canvas.pixels[y][x] = None
                else:
                    col = (r, g, b, a)
                    canvas.pixels[y][x] = col
                    unique_colors.add(col)

        char_pool = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@*+=%:abcdefghijklmnopqrstuvwxyz"
        char_idx = 0
        for col in unique_colors:
            char = char_pool[char_idx % len(char_pool)]
            palette.add(char, col)
            char_idx += 1

        canvas.palette = palette
        return canvas


    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get_pixel(self, x: int, y: int) -> Optional[RGBA]:
        if self.in_bounds(x, y):
            return self.pixels[y][x]
        return None

    def set_pixel(self, x: int, y: int, color: ColorInput) -> "Canvas":
        if self.in_bounds(x, y):
            self.pixels[y][x] = self.resolve_color(color)
        return self

    draw_pixel = set_pixel


    def draw_line(self, x0: int, y0: int, x1: int, y1: int, color: ColorInput) -> "Canvas":
        """Bresenham's line algorithm for crisp, pixel-perfect 1px lines."""
        parsed = self.resolve_color(color)
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        x, y = x0, y0
        while True:
            if self.in_bounds(x, y):
                self.pixels[y][x] = parsed
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        return self

    def draw_rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        color: ColorInput,
        fill: bool = True,
    ) -> "Canvas":
        """Draw filled or outlined rectangle."""
        parsed = self.resolve_color(color)
        x_end = min(self.width, x + w)
        y_end = min(self.height, y + h)

        if fill:
            for py in range(max(0, y), y_end):
                for px in range(max(0, x), x_end):
                    self.pixels[py][px] = parsed
        else:
            for px in range(max(0, x), x_end):
                if self.in_bounds(px, y):
                    self.pixels[y][px] = parsed
                if self.in_bounds(px, y + h - 1):
                    self.pixels[y + h - 1][px] = parsed
            for py in range(max(0, y), y_end):
                if self.in_bounds(x, py):
                    self.pixels[py][x] = parsed
                if self.in_bounds(x + w - 1, py):
                    self.pixels[py][x + w - 1] = parsed
        return self

    def draw_circle(
        self,
        cx: int,
        cy: int,
        radius: int,
        color: ColorInput,
        fill: bool = True,
    ) -> "Canvas":
        """Draw pixel-perfect circle (Midpoint / Bresenham algorithm)."""
        parsed = self.resolve_color(color)
        if radius < 0:
            return self
        if radius == 0:
            self.set_pixel(cx, cy, parsed)
            return self

        f = 1 - radius
        ddf_x = 1
        ddf_y = -2 * radius
        x = 0
        y = radius

        points: Set[Tuple[int, int]] = set()

        def add_sym(px: int, py: int):
            if fill:
                for cur_x in range(cx - px, cx + px + 1):
                    points.add((cur_x, cy + py))
                    points.add((cur_x, cy - py))
                for cur_x in range(cx - py, cx + py + 1):
                    points.add((cur_x, cy + px))
                    points.add((cur_x, cy - px))
            else:
                points.add((cx + px, cy + py))
                points.add((cx - px, cy + py))
                points.add((cx + px, cy - py))
                points.add((cx - px, cy - py))
                points.add((cx + py, cy + px))
                points.add((cx - py, cy + px))
                points.add((cx + py, cy - px))
                points.add((cx - py, cy - px))

        add_sym(x, y)

        while x < y:
            if f >= 0:
                y -= 1
                ddf_y += 2
                f += ddf_y
            x += 1
            ddf_x += 2
            f += ddf_x
            add_sym(x, y)

        for px, py in points:
            if self.in_bounds(px, py):
                self.pixels[py][px] = parsed
        return self

    def draw_ellipse(
        self,
        cx: int,
        cy: int,
        rx: int,
        ry: int,
        color: ColorInput,
        fill: bool = True,
    ) -> "Canvas":
        """Draw an ellipse (ideal for heads, shields, bubbles, puddles)."""
        parsed = self.resolve_color(color)
        if rx <= 0 or ry <= 0:
            return self

        for y in range(-ry, ry + 1):
            for x in range(-rx, rx + 1):
                val = (x * x) / (rx * rx) + (y * y) / (ry * ry)
                if fill:
                    if val <= 1.0:
                        self.set_pixel(cx + x, cy + y, parsed)
                else:
                    if 0.75 <= val <= 1.25:
                        self.set_pixel(cx + x, cy + y, parsed)
        return self

    def draw_polygon(
        self,
        points: List[Tuple[int, int]],
        fill_color: ColorInput,
        outline_color: Optional[ColorInput] = None,
    ) -> "Canvas":
        """
        Scanline-rasterizes any arbitrary convex or concave polygon.
        Essential for cloaks, wings, shields, banners, rock faces, and complex armor plates.
        """
        if len(points) < 3:
            return self

        fill_parsed = self.resolve_color(fill_color)
        min_y = max(0, min(p[1] for p in points))
        max_y = min(self.height - 1, max(p[1] for p in points))

        n = len(points)
        for y in range(min_y, max_y + 1):
            nodes = []
            for i in range(n):
                p1 = points[i]
                p2 = points[(i + 1) % n]
                y1, y2 = p1[1], p2[1]
                x1, x2 = p1[0], p2[0]

                if (y1 <= y < y2) or (y2 <= y < y1):
                    x_intersect = x1 + (y - y1) * (x2 - x1) / float(y2 - y1)
                    nodes.append(x_intersect)

            nodes.sort()
            for i in range(0, len(nodes), 2):
                if i + 1 < len(nodes):
                    x_start = max(0, int(round(nodes[i])))
                    x_end = min(self.width - 1, int(round(nodes[i + 1])))
                    for x in range(x_start, x_end + 1):
                        self.set_pixel(x, y, fill_parsed)

        if outline_color is not None:
            for i in range(n):
                p1 = points[i]
                p2 = points[(i + 1) % n]
                self.draw_line(p1[0], p1[1], p2[0], p2[1], outline_color)

        return self

    def draw_thick_line(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        thickness: int,
        color: ColorInput,
    ) -> "Canvas":
        """Draw thick Bresenham line by stamping circles along the path."""
        if thickness <= 1:
            return self.draw_line(x0, y0, x1, y1, color)

        parsed = self.resolve_color(color)
        r = thickness // 2
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy

        x, y = x0, y0
        while True:
            self.draw_circle(x, y, r, parsed, fill=True)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy
        return self

    def draw_shaded_sphere(
        self,
        cx: int,
        cy: int,
        radius: int,
        ramp: List[ColorInput],
        light_dir: Tuple[float, float] = (-0.577, -0.577),
    ) -> "Canvas":
        """
        Procedurally shades a 3D sphere with accurate spherical normals and lighting.
        ramp: Ordered list of colors from shadow -> base -> highlight (e.g. 4-step ramp).
        light_dir: (dx, dy) 2D direction of light source (default top-left).
        """
        import math
        resolved_ramp = [self.resolve_color(c) for c in ramp]
        num_steps = len(resolved_ramp)
        if num_steps == 0:
            return self

        lx, ly = light_dir
        lz = 0.577
        l_len = math.sqrt(lx * lx + ly * ly + lz * lz)
        lx, ly, lz = lx / l_len, ly / l_len, lz / l_len

        r2 = radius * radius
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                dist2 = dx * dx + dy * dy
                if dist2 <= r2:
                    dz = math.sqrt(r2 - dist2)
                    nx = dx / float(radius)
                    ny = dy / float(radius)
                    nz = dz / float(radius)

                    dot = nx * lx + ny * ly + nz * lz
                    norm_dot = max(0.0, min(1.0, (dot + 0.2) / 1.2))
                    ramp_idx = min(num_steps - 1, int(norm_dot * num_steps))
                    self.set_pixel(cx + dx, cy + dy, resolved_ramp[ramp_idx])

        return self

    def draw_shaded_cylinder(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        ramp: List[ColorInput],
        orientation: str = "vertical",
    ) -> "Canvas":
        """
        Draws a cylinder/pillar with smooth horizontal or vertical shading bands.
        Perfect for giant blades, columns, armor limbs, and pipes.
        """
        resolved_ramp = [self.resolve_color(c) for c in ramp]
        num_steps = len(resolved_ramp)
        if num_steps == 0:
            return self

        if orientation == "vertical":
            for cx in range(w):
                t = cx / float(max(1, w - 1))
                idx = min(num_steps - 1, int(t * num_steps))
                col = resolved_ramp[idx]
                for cy in range(h):
                    self.set_pixel(x + cx, y + cy, col)
        else:
            for cy in range(h):
                t = cy / float(max(1, h - 1))
                idx = min(num_steps - 1, int(t * num_steps))
                col = resolved_ramp[idx]
                for cx in range(w):
                    self.set_pixel(x + cx, y + cy, col)
        return self

    def draw_dither_rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        color1: ColorInput,
        color2: ColorInput,
        pattern: str = "checker",
    ) -> "Canvas":
        """
        Fill a rectangle with a retro dithering pattern (checkerboard, 25%, 75%, lines).
        Great for smooth retro gradients, metal shine, shadows, and textures.
        """
        c1 = self.resolve_color(color1)
        c2 = self.resolve_color(color2)

        for py in range(max(0, y), min(self.height, y + h)):
            for px in range(max(0, x), min(self.width, x + w)):
                if pattern in ("checker", "50%"):
                    pick_c1 = (px + py) % 2 == 0
                elif pattern in ("sparse", "25%"):
                    pick_c1 = (px % 2 == 0) and (py % 2 == 0)
                elif pattern in ("dense", "75%"):
                    pick_c1 = not ((px % 2 == 1) and (py % 2 == 1))
                elif pattern == "hlines":
                    pick_c1 = py % 2 == 0
                elif pattern == "vlines":
                    pick_c1 = px % 2 == 0
                elif pattern == "diag_right":
                    pick_c1 = (px + py) % 3 == 0
                else:
                    pick_c1 = (px + py) % 2 == 0

                self.pixels[py][px] = c1 if pick_c1 else c2
        return self

    def flood_fill(self, x: int, y: int, color: ColorInput) -> "Canvas":
        """4-way flood fill starting from (x, y)."""
        if not self.in_bounds(x, y):
            return self
        target_color = self.pixels[y][x]
        replacement = self.resolve_color(color)
        if target_color == replacement:
            return self

        queue = [(x, y)]
        visited = set()

        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))

            if self.pixels[cy][cx] == target_color:
                self.pixels[cy][cx] = replacement
                for nx, ny in [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]:
                    if self.in_bounds(nx, ny) and (nx, ny) not in visited:
                        if self.pixels[ny][nx] == target_color:
                            queue.append((nx, ny))
        return self


    def clone(self) -> "Canvas":
        """Return an independent deep copy of this Canvas."""
        new_c = Canvas(self.width, self.height, palette=self.palette)
        new_c.pixels = [list(row) for row in self.pixels]
        return new_c

    def auto_outline(self, color: ColorInput, diagonal: bool = True) -> "Canvas":
        """
        Generate a 1-pixel border around all non-transparent pixels.
        Returns a new Canvas with the outline placed behind or around the sprite.
        Crucial for making pixel-art sprites pop against any background.
        """
        outline_color = self.resolve_color(color)
        result = self.clone()

        offsets = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if diagonal:
            offsets += [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] is None:
                    has_opaque_neighbor = False
                    for dx, dy in offsets:
                        nx, ny = x + dx, y + dy
                        if self.in_bounds(nx, ny) and self.pixels[ny][nx] is not None:
                            has_opaque_neighbor = True
                            break
                    if has_opaque_neighbor:
                        result.pixels[y][x] = outline_color

        return result

    def auto_shadow(
        self,
        dx: int = 1,
        dy: int = 1,
        shadow_color: ColorInput = (0, 0, 0, 120),
    ) -> "Canvas":
        """
        Creates a drop-shadow offset underneath all opaque pixels.
        """
        s_color = self.resolve_color(shadow_color)
        result = Canvas(self.width, self.height, palette=self.palette)

        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] is not None:
                    sx, sy = x + dx, y + dy
                    if result.in_bounds(sx, sy):
                        result.pixels[sy][sx] = s_color

        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] is not None:
                    result.pixels[y][x] = self.pixels[y][x]

        return result

    def flip_h(self) -> "Canvas":
        """Horizontal flip (mirror left-to-right)."""
        result = Canvas(self.width, self.height, palette=self.palette)
        for y in range(self.height):
            result.pixels[y] = list(reversed(self.pixels[y]))
        return result

    def mirror_horizontal(self, from_side: str = "left", center_col: Optional[int] = None) -> "Canvas":
        """
        Mirrors one side across the vertical axis in-place.
        from_side: 'left' (copies left half over to right) or 'right'.
        center_col: Center axis column index. Defaults to (self.width - 1) / 2.
        Essential for procedural character/monster generation: draw left half procedurally, then mirror!
        """
        w = self.width
        if center_col is None:
            mid = w // 2
            for y in range(self.height):
                for x in range(mid):
                    opposite_x = w - 1 - x
                    if from_side == "left":
                        self.pixels[y][opposite_x] = self.pixels[y][x]
                    else:
                        self.pixels[y][x] = self.pixels[y][opposite_x]
        else:
            for y in range(self.height):
                for x in range(self.width):
                    if from_side == "left" and x < center_col:
                        opp = 2 * center_col - x
                        if self.in_bounds(opp, y):
                            self.pixels[y][opp] = self.pixels[y][x]
                    elif from_side == "right" and x > center_col:
                        opp = 2 * center_col - x
                        if self.in_bounds(opp, y):
                            self.pixels[y][opp] = self.pixels[y][x]
        return self

    def flip_v(self) -> "Canvas":
        """Vertical flip (upside down)."""
        result = Canvas(self.width, self.height)
        for y in range(self.height):
            result.pixels[y] = list(self.pixels[self.height - 1 - y])
        return result

    def rotate_90(self, clockwise: bool = True) -> "Canvas":
        """Rotate canvas by 90 degrees."""
        result = Canvas(self.height, self.width)
        for y in range(self.height):
            for x in range(self.width):
                if clockwise:
                    result.pixels[x][self.height - 1 - y] = self.pixels[y][x]
                else:
                    result.pixels[self.width - 1 - x][y] = self.pixels[y][x]
        return result

    def replace_color(self, old_color: ColorInput, new_color: ColorInput) -> "Canvas":
        """Replace all occurrences of old_color with new_color in-place."""
        c_old = parse_color(old_color)
        c_new = parse_color(new_color)
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] == c_old:
                    self.pixels[y][x] = c_new
        return self

    def shift_region(
        self,
        rect: Tuple[int, int, int, int],
        dx: int,
        dy: int,
        clear_original: bool = True,
    ) -> "Canvas":
        """
        Move a rectangular region (x, y, w, h) by (dx, dy).
        Essential for procedural sub-pixel animation (e.g. bobbing head, shifting hands).
        """
        rx, ry, rw, rh = rect
        region_pixels = []
        for py in range(ry, ry + rh):
            row = []
            for px in range(rx, rx + rw):
                row.append(self.get_pixel(px, py))
            region_pixels.append(row)

        if clear_original:
            for py in range(ry, ry + rh):
                for px in range(rx, rx + rw):
                    if self.in_bounds(px, py):
                        self.pixels[py][px] = None

        for row_idx, row in enumerate(region_pixels):
            for col_idx, col_val in enumerate(row):
                target_x = rx + col_idx + dx
                target_y = ry + row_idx + dy
                if self.in_bounds(target_x, target_y) and col_val is not None:
                    self.pixels[target_y][target_x] = col_val

        return self

    def paste(
        self,
        other: "Canvas",
        x: int = 0,
        y: int = 0,
        blend_alpha: bool = True,
    ) -> "Canvas":
        """Composite another Canvas onto this one at position (x, y)."""
        for oy in range(other.height):
            for ox in range(other.width):
                src_color = other.pixels[oy][ox]
                if src_color is None:
                    continue
                tx, ty = x + ox, y + oy
                if not self.in_bounds(tx, ty):
                    continue

                if not blend_alpha or src_color[3] == 255:
                    self.pixels[ty][tx] = src_color
                else:
                    bg = self.pixels[ty][tx]
                    if bg is None or bg[3] == 0:
                        self.pixels[ty][tx] = src_color
                    else:
                        sa = src_color[3] / 255.0
                        da = bg[3] / 255.0 * (1.0 - sa)
                        oa = sa + da
                        if oa > 0:
                            nr = int((src_color[0] * sa + bg[0] * da) / oa)
                            ng = int((src_color[1] * sa + bg[1] * da) / oa)
                            nb = int((src_color[2] * sa + bg[2] * da) / oa)
                            na = int(oa * 255)
                            self.pixels[ty][tx] = (nr, ng, nb, na)
        return self

    def get_silhouette(self) -> "Canvas":
        """
        Returns a 1-bit silhouette Canvas where all non-transparent pixels
        are solid black (#000000) and transparent pixels remain None.
        Essential for the Pixel Art 'Squint Test' to verify readability of the shape.
        """
        sil = Canvas(self.width, self.height)
        black: RGBA = (0, 0, 0, 255)
        for y in range(self.height):
            for x in range(self.width):
                if self.pixels[y][x] is not None and self.pixels[y][x][3] > 0:
                    sil.pixels[y][x] = black
        return sil

    def render_silhouette_text(self) -> str:
        """
        Renders a plain ASCII 1-bit silhouette (█ for solid, · for background).
        Allows AI to instantly verify the silhouette and negative space in text!
        """
        lines = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                px = self.pixels[y][x]
                if px is not None and px[3] > 0:
                    row.append("█")
                else:
                    row.append("·")
            lines.append("".join(row))
        return "\n".join(lines)

    def to_ascii(self, mapping: Optional[Dict[str, Optional[RGBA]]] = None) -> str:
        """
        Convert this canvas back to an ASCII string grid.
        Useful for inspecting or round-tripping sprite edits.
        """
        reverse_map: Dict[Optional[RGBA], str] = {None: "."}
        char_pool = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@*+=%:"
        char_idx = 0

        if mapping:
            for char_key, rgba in mapping.items():
                reverse_map[rgba] = char_key

        lines = []
        for y in range(self.height):
            line_chars = []
            for x in range(self.width):
                color = self.pixels[y][x]
                if color not in reverse_map:
                    if char_idx < len(char_pool):
                        reverse_map[color] = char_pool[char_idx]
                        char_idx += 1
                    else:
                        reverse_map[color] = "?"
                line_chars.append(reverse_map[color])
            lines.append("".join(line_chars))

        return "\n".join(lines)

    def to_ascii_definition(self) -> Tuple[str, Dict[str, str]]:
        """
        Deconstructs the sprite into an editable ASCII string grid AND a palette dictionary.
        Returns:
            (ascii_grid_string, {token: hex_color})
        The AI can directly read the exact matrix, modify a few characters, and re-create the sprite!
        """
        reverse_map: Dict[Optional[RGBA], str] = {None: "."}
        palette_dict: Dict[str, str] = {".": "transparent"}
        char_pool = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#@*+=%:abcdefghijklmnopqrstuvwxyz"
        char_idx = 0

        for y in range(self.height):
            for x in range(self.width):
                col = self.pixels[y][x]
                if col not in reverse_map:
                    char = char_pool[char_idx % len(char_pool)]
                    char_idx += 1
                    reverse_map[col] = char
                    palette_dict[char] = rgba_to_hex(col, include_alpha=True)

        lines = []
        for y in range(self.height):
            row = [reverse_map[self.pixels[y][x]] for x in range(self.width)]
            lines.append("".join(row))

        return "\n".join(lines), palette_dict

    def palette_swap(self, swap_map: Dict[ColorInput, ColorInput]) -> "Canvas":
        """
        Swap multiple colors at once across the entire canvas.
        Essential for creating element variants (e.g. Green Slime -> Fire Slime / Ice Slime),
        team colors (Red Knight -> Blue Knight), or shiny variants!
        """
        result = self.clone()
        resolved_map: Dict[RGBA, Optional[RGBA]] = {}
        for src, dst in swap_map.items():
            src_rgba = self.resolve_color(src)
            dst_rgba = self.resolve_color(dst)
            if src_rgba is not None:
                resolved_map[src_rgba] = dst_rgba

        for y in range(result.height):
            for x in range(result.width):
                px = result.pixels[y][x]
                if px in resolved_map:
                    result.pixels[y][x] = resolved_map[px]
        return result

    def crop(self, x: int, y: int, width: int, height: int) -> "Canvas":
        """Crop a sub-region into a new Canvas."""
        result = Canvas(width, height, palette=self.palette)
        for cy in range(height):
            for cx in range(width):
                result.pixels[cy][cx] = self.get_pixel(x + cx, y + cy)
        return result

    def resize_canvas(
        self,
        new_width: int,
        new_height: int,
        anchor: str = "center",
        default_color: ColorInput = None,
    ) -> "Canvas":
        """
        Expands or contracts the canvas size, placing existing sprite at anchor point.
        anchor: 'center', 'top-left', 'bottom-left', 'bottom-center'
        Useful when an AI wants to add a hat, wings, or aura to a 16x16 sprite by making it 20x20.
        """
        result = Canvas(new_width, new_height, default_color=default_color, palette=self.palette)
        if anchor == "center":
            ox = (new_width - self.width) // 2
            oy = (new_height - self.height) // 2
        elif anchor == "top-left":
            ox, oy = 0, 0
        elif anchor == "bottom-center":
            ox = (new_width - self.width) // 2
            oy = new_height - self.height
        elif anchor == "bottom-left":
            ox = 0
            oy = new_height - self.height
        else:
            ox, oy = 0, 0

        result.paste(self, x=ox, y=oy, blend_alpha=True)
        return result


class LayeredCanvas:
    """
    Manages multiple named Canvas layers.
    Allows independent drawing and animating of parts (e.g. body, clothes, weapon, eyes).
    """

    def __init__(self, width: int, height: int, palette: Optional[Palette] = None):
        self.width = width
        self.height = height
        self.palette = palette
        self._layers: Dict[str, Canvas] = {}
        self._order: List[str] = []
        self._visible: Dict[str, bool] = {}

    def add_layer(self, name: str, canvas: Optional[Canvas] = None) -> Canvas:
        """Add a layer. If no canvas provided, creates a blank one."""
        if name in self._layers:
            raise ValueError(f"Layer '{name}' already exists.")
        if canvas is None:
            canvas = Canvas(self.width, self.height, palette=self.palette)
        else:
            if canvas.width != self.width or canvas.height != self.height:
                raise ValueError(
                    f"Layer dimensions {canvas.width}x{canvas.height} don't match canvas {self.width}x{self.height}"
                )
            if canvas.palette is None and self.palette is not None:
                canvas.palette = self.palette
        self._layers[name] = canvas
        self._order.append(name)
        self._visible[name] = True
        return canvas

    def get_layer(self, name: str) -> Canvas:
        if name not in self._layers:
            raise KeyError(f"Layer '{name}' not found. Available: {self._order}")
        return self._layers[name]

    def set_visible(self, name: str, visible: bool) -> "LayeredCanvas":
        if name in self._visible:
            self._visible[name] = visible
        return self

    def flatten(self) -> Canvas:
        """Composite all visible layers in order from bottom to top into a single Canvas."""
        result = Canvas(self.width, self.height, palette=self.palette)
        for name in self._order:
            if self._visible.get(name, True):
                result.paste(self._layers[name], x=0, y=0, blend_alpha=True)
        return result

    def clone(self) -> "LayeredCanvas":
        """Deep copy of the entire layered canvas."""
        new_lc = LayeredCanvas(self.width, self.height, palette=self.palette)
        for name in self._order:
            new_lc._layers[name] = self._layers[name].clone()
            new_lc._order.append(name)
            new_lc._visible[name] = self._visible[name]
        return new_lc
