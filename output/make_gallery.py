"""
Generate a consolidated HTML Gallery showing all sprites with zoom controls.
"""
from pixelcraft import export_gallery

if __name__ == "__main__":
    out = export_gallery("output")
    print(f"Gallery updated: {out}")
