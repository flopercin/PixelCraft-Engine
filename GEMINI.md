# Workspace Guidelines: 2D Pixel Art & Sprites

Whenever the user requests 2D sprites, pixel art, game assets, icons, characters, weapons, or retro animations in this workspace:

1. **NEVER use the `generate_image` tool** (diffusion model). Diffusion models cannot generate true grid-aligned pixel art, cannot be edited via code, and introduce blurry non-retro artifacts.
2. **ALWAYS use the `pixelcraft` skill with PROCEDURAL GEOMETRIC GENERATION as the PRIMARY & RECOMMENDED approach**:
   - Construct sprites using procedural primitives: `draw_shaded_sphere`, `draw_shaded_cylinder`, `draw_polygon`, `draw_thick_line`, and `mirror_horizontal`.
   - **Why Procedural is Default:** It produces significantly higher visual quality (true 3D volume, smooth lighting ramps), consumes 4–5x fewer tokens, and eliminates ASCII line-drift errors.
   - ASCII matrices are only a secondary fallback for tiny 16×16 micro-icons.
   - Always run the script, inspect the result via `view_file` on `output/..._preview.png`, and verify using `lint_sprite`.
3. **ZERO PIXELCRAFT LIBRARY RECONNAISSANCE:**
   - DO NOT inspect `pixelcraft/` source code or `examples/` trying to learn the API — all APIs, imports, and templates are fully self-contained in the `pixelcraft` SKILL.md.
   - Write the generator script immediately in one step.
   - *(Note: Normal filesystem operations and exploration are fully permitted when integrating sprites into a game project, locating assets directories, or copying files into Godot/Unity/etc.)*
4. **STRICT SCOPE COMPLIANCE:**
   - If the user asks for a **sprite**, generate **ONLY that single static sprite** (`output/<name>.png`).
   - NEVER generate animations, GIFs, spritesheets, JSON metadata, or extra unrequested variants unless explicitly asked!
   - Save the script cleanly in `output/generate_<name>.py`.
