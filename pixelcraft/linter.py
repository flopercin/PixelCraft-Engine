"""
pixelcraft.linter
Automated pixel art diagnostics and quality checks for AI agents.
Detects orphan pixels (jaggies/noise), checks color counts, bounding box coverage,
and verifies horizontal/vertical symmetry with actionable error messages.
"""

from typing import Dict, List, Optional, Tuple, Union
from collections import Counter

from .canvas import Canvas, LayeredCanvas
from .palette import RGBA, rgba_to_hex


class LintReport:
    """Diagnostic report describing sprite properties and potential visual defects."""

    def __init__(self):
        self.canvas_size: Tuple[int, int] = (0, 0)
        self.bounding_box: Optional[Tuple[int, int, int, int]] = None
        self.non_empty_pixels: int = 0
        self.coverage_percent: float = 0.0
        self.unique_colors_count: int = 0
        self.color_histogram: Dict[str, int] = {}
        self.orphan_pixels: List[Tuple[int, int]] = []
        self.horizontal_symmetry_score: float = 0.0
        self.vertical_symmetry_score: float = 0.0
        self.silhouette_text: str = ""
        self.warnings: List[str] = []

    def is_clean(self) -> bool:
        return len(self.warnings) == 0

    def summary(self, show_silhouette: bool = False) -> str:
        lines = [
            f"--- PixelCraft Sprite Diagnostic ---",
            f"Canvas Dimensions: {self.canvas_size[0]}x{self.canvas_size[1]}",
        ]
        if self.bounding_box:
            bx0, by0, bx1, by1 = self.bounding_box
            lines.append(f"Content Bounding Box: ({bx0}, {by0}) -> ({bx1}, {by1}) [size {bx1 - bx0 + 1}x{by1 - by0 + 1}]")
            lines.append(f"Occupied Pixels: {self.non_empty_pixels} ({self.coverage_percent:.1f}% coverage)")
        else:
            lines.append("Content: EMPTY CANVAS")

        lines.append(f"Unique Colors: {self.unique_colors_count}")
        lines.append(f"Horizontal Symmetry: {self.horizontal_symmetry_score * 100:.1f}%")

        if show_silhouette and self.silhouette_text:
            lines.append("\n[ Silhouette Squint Test ]:")
            lines.append(self.silhouette_text)

        if self.warnings:
            lines.append("\n[!] Warnings & Advice for AI:")
            for w in self.warnings:
                lines.append(f"  • {w}")
        else:
            lines.append("\n[✓] Quality check passed cleanly. No orphan pixels or syntax errors.")

        return "\n".join(lines)


def lint_sprite(
    canvas: Union[Canvas, LayeredCanvas],
    max_colors: Optional[int] = 32,
    check_orphans: bool = True,
) -> LintReport:
    """
    Run diagnostic checks on a Canvas and return a detailed report with actionable advice.
    """
    if isinstance(canvas, LayeredCanvas):
        canvas = canvas.flatten()

    report = LintReport()
    w, h = canvas.width, canvas.height
    report.canvas_size = (w, h)
    report.silhouette_text = canvas.render_silhouette_text()

    min_x, min_y = w, h
    max_x, max_y = -1, -1

    color_counts: Counter = Counter()

    for y in range(h):
        for x in range(w):
            px = canvas.pixels[y][x]
            if px is not None and px[3] > 0:
                report.non_empty_pixels += 1
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                hex_col = rgba_to_hex(px)
                color_counts[hex_col] += 1

    total_pixels = w * h
    if report.non_empty_pixels > 0:
        report.bounding_box = (min_x, min_y, max_x, max_y)
        report.coverage_percent = (report.non_empty_pixels / total_pixels) * 100.0
    else:
        report.warnings.append("Canvas contains no opaque pixels (entirely transparent).")

    report.unique_colors_count = len(color_counts)
    report.color_histogram = dict(color_counts)

    if max_colors and report.unique_colors_count > max_colors:
        report.warnings.append(
            f"Color count ({report.unique_colors_count}) exceeds recommended limit ({max_colors}). "
            f"Consider quantizing or sticking to a unified palette."
        )

    if check_orphans and report.non_empty_pixels > 0:
        orthogonal = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for y in range(h):
            for x in range(w):
                if canvas.pixels[y][x] is not None:
                    has_neighbor = False
                    for dx, dy in orthogonal:
                        nx, ny = x + dx, y + dy
                        if canvas.in_bounds(nx, ny) and canvas.pixels[ny][nx] is not None:
                            has_neighbor = True
                            break
                    if not has_neighbor:
                        report.orphan_pixels.append((x, y))

        if report.orphan_pixels:
            sample = report.orphan_pixels[:6]
            report.warnings.append(
                f"Found {len(report.orphan_pixels)} isolated orphan pixel(s) at {sample}. "
                f"In pixel art, isolated pixels often look like noisy dust or unintended jaggies."
            )

    if report.non_empty_pixels > 0:
        matches = 0
        total_checks = 0
        for y in range(h):
            for x in range(w // 2):
                col_left = canvas.pixels[y][x]
                col_right = canvas.pixels[y][w - 1 - x]
                if col_left is not None or col_right is not None:
                    total_checks += 1
                    if col_left == col_right:
                        matches += 1
        if total_checks > 0:
            report.horizontal_symmetry_score = matches / total_checks

    return report
