#!/usr/bin/env python3
"""Packs the app's room art into web assets for the landing page's live room (assets/room.js).

Reads the Kachingz app's Resources/Mochi folder and writes assets/room/: the room at each time of day,
its lamp, fishbowl, chair, furniture and weather art, the fan as one sprite sheet, and each cat's
looping clips as sprite sheets cropped to what the frames actually use. layout.json carries the
app's coordinates (a 358-unit square scene) so room.js can draw it the way MochiRoomView does.

    python3 tools/room_assets.py [path/to/Resources/Mochi]
"""
import json
import math
import pathlib
import shutil
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                   ROOT.parent / "Kaching/versions/v1.1/Kaching/Resources/Mochi")
OUT = ROOT / "assets/room"
TIMES = ["dawn", "day", "dusk", "night"]
WEATHERS = ["cloudy", "rain", "storm", "snow"]
# The loops the page plays. Frames are scaled to keep the sheets light; the cat is drawn at most
# ~200 CSS px tall, which these cover at 2x.
CLIPS = ["idle", "sitloop", "sleeploop", "joy"]
CAT_SCALE = 0.8
FAN_SCALE = 0.5
COLS = 8


def webp(src, dst, size=None, quality=80):
    im = Image.open(src)
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
    if size:
        im = im.resize(size, Image.LANCZOS)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "WEBP", quality=quality, method=6)
    return im.size


def sheet(frames, meta, scale, dst, quality=75):
    """Frames cropped to their union box, scaled and packed COLS wide. Returns the clip's layout."""
    ims = [Image.open(f).convert("RGBA") for f in frames]
    box = None
    for im in ims:
        b = im.getbbox()
        if b:
            box = b if box is None else (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    box = box or (0, 0, *ims[0].size)
    cw, ch = box[2] - box[0], box[3] - box[1]
    w, h = max(1, round(cw * scale)), max(1, round(ch * scale))
    rows = math.ceil(len(ims) / COLS)
    out = Image.new("RGBA", (w * min(COLS, len(ims)), h * rows), (0, 0, 0, 0))
    for i, im in enumerate(ims):
        out.paste(im.crop(box).resize((w, h), Image.LANCZOS), ((i % COLS) * w, (i // COLS) * h))
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst, "WEBP", quality=quality, method=6)
    # Size and feet in the clip's original pixels, so the scene's scale (height / 340) still applies.
    return {"frames": len(ims), "cols": COLS, "cw": w, "ch": h,
            "w": cw, "h": ch, "fx": meta["fx"] - box[0], "fy": meta["fy"] - box[1]}


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    manifest = json.loads((SRC / "manifest.json").read_text())
    weather = json.loads((SRC / "weather/weather.json").read_text())
    layout = {"card": manifest["card"], "height": manifest["height"], "room": manifest["room"],
              "light": manifest["light"], "chair": manifest["chair"], "furniture": manifest["furniture"],
              "weather": {"window": weather["window"], "light": weather["light"]}, "cats": {}}

    for t in TIMES:
        webp(SRC / f"room-{t}.jpg", OUT / f"room-{t}.webp", quality=82)
        for layer in ("lamp", "fishbowl"):
            webp(SRC / f"{layer}-{t}.webp", OUT / f"{layer}-{t}.webp", quality=85)
        for w in WEATHERS:
            webp(SRC / f"weather/{w}-{t}.webp", OUT / f"weather/{w}-{t}.webp", quality=85)
        for piece in manifest["furniture"]["pieces"]:
            src = SRC / f"furniture/{piece['id']}-{t}.webp"
            if src.exists():
                webp(src, OUT / f"furniture/{piece['id']}-{t}.webp", quality=85)
    webp(SRC / "chair.webp", OUT / "chair.webp", quality=85)
    webp(SRC / "weather/glass.png", OUT / "weather/glass.webp", quality=90)

    appliances = {}
    for name, a in weather["appliances"].items():
        if a["frames"] > 1:
            frames = sorted((SRC / f"weather/{name}").glob("*.webp"))
            appliances[name] = {**a, **sheet(frames, a, FAN_SCALE, OUT / f"weather/{name}.webp")}
        else:
            webp(SRC / f"weather/{name}.webp", OUT / f"weather/{name}.webp", quality=85)
            appliances[name] = {**a, "cols": 1, "cw": a["w"], "ch": a["h"]}
    layout["weather"]["appliances"] = appliances

    # The seasons: the app's decorations and costumes (tools/pet-sprites/seasons in the app repo).
    seasons = json.loads((SRC / "seasons/seasons.json").read_text())
    layout["seasons"] = {}
    for name, entry in seasons["seasons"].items():
        for t in TIMES:
            webp(SRC / f"seasons/{name}/decor-{t}.webp", OUT / f"seasons/{name}/decor-{t}.webp", quality=88)
        if entry.get("costume"):
            webp(SRC / f"seasons/{name}/costume.webp", OUT / f"seasons/{name}/costume.webp", quality=90)
        layout["seasons"][name] = entry
    layout["headScale"] = {c: v["scale"] for c, v in seasons["head"].items()}

    for cat, base in (("tabby", SRC), ("tuxedo", SRC / "cats/tuxedo")):
        clips = manifest["clips"] if cat == "tabby" else json.loads((base / "clips.json").read_text())
        layout["cats"][cat] = {}
        for clip in CLIPS:
            frames = sorted((base / clip).glob("*.webp"))
            meta = sheet(frames, clips[clip], CAT_SCALE, OUT / f"{cat}/{clip}.webp")
            # The head on each frame (where costumes go), moved into the cropped frame (same px as fx and fy).
            heads = seasons["head"][cat]["clips"].get(clip)
            if heads:
                dx, dy = clips[clip]["fx"] - meta["fx"], clips[clip]["fy"] - meta["fy"]
                meta["head"] = [[round(x - dx, 1), round(y - dy, 1), r, t] for x, y, r, t in heads]
            layout["cats"][cat][clip] = meta

    (OUT / "layout.json").write_text(json.dumps(layout, separators=(",", ":")))
    total = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file())
    print(f"wrote {OUT.relative_to(ROOT)}: {total / 1024:.0f} KB")
    for cat in ("tabby", "tuxedo"):
        print(" ", cat, {c: f"{(OUT / cat / f'{c}.webp').stat().st_size // 1024} KB" for c in CLIPS})


if __name__ == "__main__":
    main()
