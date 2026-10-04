# Workspace Guidelines: 2D Pixel Art & Procedural Sprites

Universal instructions for AI Agents (Antigravity, Claude Code, Cursor, Codex, Gemini, etc.) working in this repository:

Whenever generating or editing 2D sprites, pixel art, game assets, icons, characters, weapons, or retro animations:

1. **NEVER use diffusion models (`generate_image`)**:
   - Diffusion models cannot generate true grid-aligned pixel art, cannot be programmatically edited, and introduce blurry non-retro artifacts.

2. **ALWAYS use PROCEDURAL GEOMETRIC GENERATION as the PRIMARY & RECOMMENDED approach**:
   - Construct sprites using procedural primitives: `draw_shaded_sphere`, `draw_shaded_cylinder`, `draw_polygon`, `draw_thick_line`, `Palette.create_ramp`, and `mirror_horizontal`.
   - **Why Procedural is Default:**
     - Significantly higher artistic fidelity (true 3D volume, directional shading, smooth specular highlights).
     - 4–5x fewer tokens consumed than large ASCII text matrices.
     - Eliminates off-by-one line length errors and coordinate drift.
   - ASCII matrices (`from_ascii`, `from_ascii_symmetric`) are strictly a secondary fallback for tiny 8x8 or 16x16 micro-icons.

3. **AUTOMATIC SHOWCASE GALLERY (`gallery.html`)**:
   - When generating or batching sprites, always refresh the interactive gallery via `export_gallery("output")` or `python -m pixelcraft gallery output`.
   - This provides the user with an instant, interactive HTML gallery in `output/gallery.html` featuring zoom controls (up to 12x), background toggles (checkerboard, dark, light, green screen), and asset resolution inspection.

4. **USE THE PRE-INSTALLED AGENT SKILL**:
   - All APIs, palettes, procedural templates, and usage examples are completely documented in `.agents/skills/pixelcraft/SKILL.md`.
   - **Zero Library Reconnaissance:** Do not spend tokens reading `pixelcraft/` source code. Consult the skill directly.

5. **STRICT SCOPE COMPLIANCE**:
   - If the user asks for a single sprite, generate **ONLY that single static sprite** (`output/<name>.png`).
   - Do NOT generate extra animations, GIFs, spritesheets, or unrequested variants unless explicitly requested.
   - Save generator scripts cleanly in `output/generate_<name>.py`.
