"""
pixelcraft.animation
Animation timeline and procedural animation generators optimized for AI sprite generation.
Supports frame cloning, ping-pong looping, idle bounces, floating, squishing, and hit flashes.
"""

from typing import Callable, List, Optional, Union
import math

from .canvas import Canvas, LayeredCanvas
from .palette import ColorInput, parse_color


class Frame:
    """A single animation frame containing a Canvas and duration in milliseconds."""

    def __init__(self, canvas: Canvas, duration_ms: int = 125):
        self.canvas = canvas.clone()
        self.duration_ms = duration_ms

    def clone(self) -> "Frame":
        return Frame(self.canvas.clone(), self.duration_ms)


class Animation:
    """
    Manages an ordered sequence of animation frames.
    Can be exported as animated GIF, horizontal/vertical spritesheet, or Godot SpriteFrames.
    """

    def __init__(self, name: str = "default", default_duration_ms: int = 125):
        self.name = name
        self.default_duration_ms = default_duration_ms
        self.frames: List[Frame] = []

    def add_frame(self, canvas: Union[Canvas, LayeredCanvas], duration_ms: Optional[int] = None) -> "Animation":
        """Add a frame to the animation sequence."""
        if isinstance(canvas, LayeredCanvas):
            canvas = canvas.flatten()
        dur = duration_ms if duration_ms is not None else self.default_duration_ms
        self.frames.append(Frame(canvas, dur))
        return self

    def add_frames(self, canvases: List[Union[Canvas, LayeredCanvas]], duration_ms: Optional[int] = None) -> "Animation":
        """Add multiple frames with the same duration."""
        for c in canvases:
            self.add_frame(c, duration_ms)
        return self

    def get_frame(self, index: int) -> Canvas:
        """Get the canvas of the frame at the specified index."""
        return self.frames[index].canvas

    def __len__(self) -> int:
        return len(self.frames)

    @property
    def width(self) -> int:
        return self.frames[0].canvas.width if self.frames else 0

    @property
    def height(self) -> int:
        return self.frames[0].canvas.height if self.frames else 0

    def clone(self) -> "Animation":
        """Deep copy of this animation."""
        new_anim = Animation(self.name, self.default_duration_ms)
        for f in self.frames:
            new_anim.frames.append(f.clone())
        return new_anim

    def ping_pong(self) -> "Animation":
        """
        Convert sequence [0, 1, 2, 3] to a seamless bounce loop [0, 1, 2, 3, 2, 1].
        Modifies and returns self.
        """
        if len(self.frames) <= 2:
            return self
        for f in reversed(self.frames[1:-1]):
            self.frames.append(f.clone())
        return self

    def reversed(self) -> "Animation":
        """Return a new Animation with reversed frame order."""
        new_anim = Animation(f"{self.name}_reversed", self.default_duration_ms)
        for f in reversed(self.frames):
            new_anim.frames.append(f.clone())
        return new_anim


    @classmethod
    def create_floating(
        cls,
        base: Union[Canvas, LayeredCanvas],
        float_px: int = 2,
        frames_count: int = 6,
        duration_ms: int = 130,
        name: str = "float",
    ) -> "Animation":
        """
        Create a smooth sine-wave vertical hovering / floating animation.
        Perfect for flying characters, ghosts, bats, fairies, power-up items, and floating text.
        """
        if isinstance(base, LayeredCanvas):
            base = base.flatten()

        anim = cls(name=name, default_duration_ms=duration_ms)
        for i in range(frames_count):
            angle = (2.0 * math.pi * i) / frames_count
            offset_y = round(math.sin(angle) * float_px)
            frame_c = Canvas(base.width, base.height)
            frame_c.paste(base, x=0, y=offset_y)
            anim.add_frame(frame_c, duration_ms)

        return anim

    @classmethod
    def create_idle_bounce(
        cls,
        base: Union[Canvas, LayeredCanvas],
        bounce_px: int = 1,
        ground_hold_y: Optional[int] = None,
        duration_ms: int = 150,
        name: str = "idle",
    ) -> "Animation":
        """
        Create a classic 4-frame RPG idle breathing/bounce cycle:
        Frame 0: Normal
        Frame 1: Dip down 1px (squish/inhale)
        Frame 2: Normal
        Frame 3: Rise up 1px (stretch/exhale)
        If ground_hold_y is given, pixels at and below that line stay fixed while upper body moves.
        """
        if isinstance(base, LayeredCanvas):
            base = base.flatten()

        anim = cls(name=name, default_duration_ms=duration_ms)

        def make_offset_frame(dy: int) -> Canvas:
            if dy == 0 or ground_hold_y is None:
                c = Canvas(base.width, base.height)
                c.paste(base, x=0, y=dy)
                return c
            c = Canvas(base.width, base.height)
            for py in range(ground_hold_y, base.height):
                for px in range(base.width):
                    c.pixels[py][px] = base.pixels[py][px]
            for py in range(0, ground_hold_y):
                for px in range(base.width):
                    col = base.pixels[py][px]
                    if col is not None:
                        ny = py + dy
                        if c.in_bounds(px, ny):
                            c.pixels[ny][px] = col
            return c

        anim.add_frame(base, duration_ms)
        anim.add_frame(make_offset_frame(bounce_px), duration_ms)
        anim.add_frame(base, duration_ms)
        anim.add_frame(make_offset_frame(-bounce_px), duration_ms)

        return anim

    @classmethod
    def create_squash_and_stretch(
        cls,
        base: Union[Canvas, LayeredCanvas],
        max_squash: int = 2,
        duration_ms: int = 120,
        name: str = "squash",
    ) -> "Animation":
        """
        Squash and stretch animation (great for slimes, jumps, bounces, drops).
        """
        if isinstance(base, LayeredCanvas):
            base = base.flatten()

        anim = cls(name=name, default_duration_ms=duration_ms)

        anim.add_frame(base, duration_ms)

        f1 = Canvas(base.width, base.height)
        for y in range(base.height):
            for x in range(base.width):
                col = base.pixels[y][x]
                if col is not None:
                    sy = min(base.height - 1, int(y + max_squash))
                    f1.set_pixel(x, sy, col)
                    if x > 1 and base.pixels[y][x - 1] is None:
                        f1.set_pixel(x - 1, sy, col)
                    if x < base.width - 2 and base.pixels[y][x + 1] is None:
                        f1.set_pixel(x + 1, sy, col)
        anim.add_frame(f1, duration_ms)

        anim.add_frame(base, duration_ms)

        f3 = Canvas(base.width, base.height)
        for y in range(base.height):
            for x in range(base.width):
                col = base.pixels[y][x]
                if col is not None:
                    sy = max(0, int(y - max_squash))
                    f3.set_pixel(x, sy, col)
        anim.add_frame(f3, duration_ms)

        return anim

    @classmethod
    def create_hit_flash(
        cls,
        base: Union[Canvas, LayeredCanvas],
        flash_color: ColorInput = "#ffffff",
        flashes: int = 2,
        duration_ms: int = 80,
        name: str = "hit",
    ) -> "Animation":
        """
        Damage hit flash animation: toggles between solid flash color and original sprite.
        """
        if isinstance(base, LayeredCanvas):
            base = base.flatten()

        flash_c = Canvas(base.width, base.height)
        parsed_flash = parse_color(flash_color)
        for y in range(base.height):
            for x in range(base.width):
                if base.pixels[y][x] is not None:
                    flash_c.pixels[y][x] = parsed_flash

        anim = cls(name=name, default_duration_ms=duration_ms)
        for _ in range(flashes):
            anim.add_frame(flash_c, duration_ms)
            anim.add_frame(base, duration_ms)

        return anim
