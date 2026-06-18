from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "world-footprint-dot-map.png"
PREVIEW = Path("/private/tmp/world-footprint-dot-preview.png")
GEOKIT_WORLD_MAP = Path("/System/Library/PrivateFrameworks/GeoKit.framework/Versions/A/Resources/worldmap@2x.png")

W, H = 3600, 1530
LON_MIN, LON_MAX = -180, 180
LAT_MIN, LAT_MAX = -58, 83
SCALE = 3
RNG = random.Random(20260610)


def project(point: tuple[float, float], scale: int = SCALE) -> tuple[int, int]:
    lon, lat = point
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * W
    y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * H
    return round(x * scale), round(y * scale)


def geo_project(point: tuple[float, float]) -> tuple[int, int]:
    lon, lat = point
    if GEOKIT_WORLD_MAP.exists():
        x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * W
        y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * H
        return round(x), round(y)
    x, y = project(point, scale=1)
    return x, y


def draw_poly(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill: int = 255) -> None:
    draw.polygon([project(p) for p in points], fill=fill)


def draw_ellipse_lonlat(
    draw: ImageDraw.ImageDraw,
    lon: float,
    lat: float,
    rx: float,
    ry: float,
    fill: int = 255,
) -> None:
    x1, y1 = project((lon - rx, lat + ry))
    x2, y2 = project((lon + rx, lat - ry))
    draw.ellipse([x1, y1, x2, y2], fill=fill)


def make_land_mask() -> Image.Image:
    if GEOKIT_WORLD_MAP.exists():
        src = Image.open(GEOKIT_WORLD_MAP).convert("RGBA").getchannel("A")
        solid = src.point(lambda p: 255 if p > 36 else 0)
        bbox = solid.getbbox() or (0, 0, src.width, src.height)
        crop = src.crop((bbox[0], max(0, bbox[1] - 8), bbox[2], min(src.height, bbox[3] + 10)))
        crop = crop.point(lambda p: 255 if p > 18 else 0)
        return crop.resize((W, H), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(0.35))

    mask = Image.new("L", (W * SCALE, H * SCALE), 0)
    draw = ImageDraw.Draw(mask)

    # North America, including Alaska and Central America.
    draw_poly(draw, [
        (-168, 71), (-156, 72), (-143, 70), (-135, 65), (-127, 60),
        (-123, 53), (-130, 50), (-124, 45), (-125, 39), (-117, 34),
        (-111, 31), (-107, 25), (-98, 22), (-91, 18), (-86, 15),
        (-83, 10), (-78, 9), (-75, 12), (-77, 18), (-82, 24),
        (-81, 29), (-75, 34), (-69, 40), (-58, 47), (-52, 52),
        (-61, 56), (-75, 57), (-88, 62), (-103, 61), (-111, 66),
        (-123, 69), (-139, 71), (-154, 70), (-168, 66)
    ])
    draw_poly(draw, [
        (-169, 61), (-153, 60), (-142, 56), (-137, 50), (-145, 48),
        (-155, 54), (-166, 55)
    ])
    draw_poly(draw, [
        (-113, 31), (-106, 28), (-100, 24), (-94, 20), (-90, 17),
        (-87, 14), (-91, 14), (-99, 18), (-106, 22), (-112, 27)
    ])
    draw_poly(draw, [
        (-84, 21), (-79, 22), (-76, 20), (-74, 18), (-77, 15), (-82, 17)
    ])

    # Greenland and Arctic islands.
    draw_poly(draw, [
        (-73, 78), (-50, 83), (-26, 80), (-18, 72), (-27, 63),
        (-44, 60), (-61, 65), (-72, 72)
    ])
    for lon, lat, rx, ry in [(-100, 74, 7, 3), (-82, 72, 5, 2), (-18, 65, 4, 2)]:
        draw_ellipse_lonlat(draw, lon, lat, rx, ry)

    # South America.
    draw_poly(draw, [
        (-81, 12), (-74, 11), (-68, 8), (-61, 6), (-54, 1),
        (-47, -4), (-41, -12), (-36, -19), (-40, -26), (-45, -31),
        (-48, -39), (-55, -51), (-63, -55), (-70, -46), (-73, -35),
        (-75, -26), (-78, -18), (-81, -8), (-79, 0), (-82, 6)
    ])

    # Europe.
    draw_poly(draw, [
        (-11, 36), (-7, 44), (-9, 51), (-2, 56), (8, 60), (20, 60),
        (28, 56), (32, 50), (40, 47), (38, 42), (29, 39), (20, 40),
        (12, 45), (5, 43), (-3, 40)
    ])
    draw_poly(draw, [(-8, 58), (1, 60), (8, 57), (2, 53), (-5, 54)])
    draw_poly(draw, [(12, 55), (23, 59), (31, 56), (30, 50), (18, 51)])
    draw_ellipse_lonlat(draw, -3, 54, 3.4, 5.8)
    draw_ellipse_lonlat(draw, -18, 65, 4.5, 2.5)

    # Africa.
    draw_poly(draw, [
        (-18, 35), (-5, 37), (10, 36), (24, 33), (34, 27), (43, 12),
        (51, 8), (49, -7), (42, -17), (35, -25), (31, -34),
        (21, -35), (13, -29), (8, -35), (-2, -32), (-10, -24),
        (-15, -12), (-17, 0), (-13, 12), (-16, 25)
    ])
    draw_poly(draw, [(48, -12), (51, -17), (49, -25), (45, -25), (43, -17)])

    # Asia mainland.
    draw_poly(draw, [
        (31, 71), (54, 74), (82, 72), (108, 69), (136, 66), (161, 61),
        (179, 58), (179, 48), (166, 46), (151, 43), (139, 43),
        (130, 38), (122, 40), (113, 35), (106, 27), (99, 22),
        (95, 15), (100, 8), (103, 1), (99, -5), (91, 8),
        (84, 20), (76, 26), (69, 28), (61, 35), (51, 32),
        (43, 26), (38, 17), (32, 14), (31, 24), (26, 35), (30, 45),
        (38, 51), (31, 60)
    ])
    # Arabian Peninsula, India and Southeast Asia are drawn over the mainland
    # to keep recognizable silhouettes after dot sampling.
    draw_poly(draw, [
        (35, 31), (48, 30), (57, 23), (56, 15), (48, 13), (40, 17), (34, 25)
    ])
    draw_poly(draw, [
        (68, 25), (78, 24), (87, 20), (88, 13), (83, 7), (78, 5),
        (73, 10), (69, 17)
    ])
    draw_poly(draw, [
        (95, 23), (104, 21), (110, 15), (109, 8), (105, 3), (101, -4),
        (96, 5), (94, 14)
    ])
    # Korea, Japan, Philippines, Indonesia.
    draw_ellipse_lonlat(draw, 127, 38, 3, 5)
    for lon, lat, rx, ry in [(139, 38, 2.8, 7.8), (143, 43, 2.4, 4), (131, 32, 1.8, 3)]:
        draw_ellipse_lonlat(draw, lon, lat, rx, ry)
    for lon, lat, rx, ry in [(121, 14, 2.8, 6), (124, 9, 3.5, 4.5), (119, 5, 2.2, 3.4)]:
        draw_ellipse_lonlat(draw, lon, lat, rx, ry)
    for lon, lat, rx, ry in [(105, -5, 8, 2.8), (116, -2, 8, 3), (121, -7, 6, 3),
                             (131, -3, 8, 3), (139, -5, 5, 2.4)]:
        draw_ellipse_lonlat(draw, lon, lat, rx, ry)

    # Australia and New Zealand.
    draw_poly(draw, [
        (112, -11), (124, -13), (137, -11), (151, -20), (153, -31),
        (145, -39), (131, -38), (119, -33), (112, -24)
    ])
    draw_ellipse_lonlat(draw, 146, -42, 4, 2.5)
    draw_ellipse_lonlat(draw, 172, -42, 2.2, 5)

    # Important islands that help the map read as complete.
    for lon, lat, rx, ry in [
        (-6, 53, 2.5, 4), (15, 41, 3.8, 5.5), (23, 39, 3.5, 2.2),
        (33, 35, 2.2, 1.8), (80, 7, 1.9, 3.8), (101, 0, 3.4, 2),
        (121, 24, 2.2, 2.8), (-61, 15, 2.4, 1.8), (-71, 19, 2.8, 1.8),
        (-77, 18, 3.8, 1.5), (-8, 28, 2, 2), (44, -19, 2.8, 6)
    ]:
        draw_ellipse_lonlat(draw, lon, lat, rx, ry)

    return mask.filter(ImageFilter.GaussianBlur(0.9 * SCALE)).resize((W, H), Image.Resampling.LANCZOS)


def alpha_at(mask: Image.Image, x: int, y: int) -> int:
    if x < 0 or y < 0 or x >= W or y >= H:
        return 0
    return mask.getpixel((x, y))


def draw_glow(layer: Image.Image, x: float, y: float, radius: int, color: tuple[int, int, int], strength: int) -> None:
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(5, 0, -1):
        r = radius * i / 5
        a = int(strength * (i / 5) ** 2)
        gd.ellipse([x - r, y - r, x + r, y + r], fill=(*color, a))
    glow = glow.filter(ImageFilter.GaussianBlur(radius * 0.34))
    layer.alpha_composite(glow)
    d = ImageDraw.Draw(layer)
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(239, 255, 218, 230))


def add_land_sparkles(layer: Image.Image, mask: Image.Image) -> None:
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    points = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(points)

    for _ in range(120):
        x = RNG.randrange(24, W - 24)
        y = RNG.randrange(24, H - 24)
        a = alpha_at(mask, x, y)
        if a < 160:
            continue
        radius = RNG.uniform(6, 13)
        strength = RNG.randrange(16, 36)
        color = RNG.choice([(206, 244, 181), (175, 228, 145), (230, 255, 210)])
        gd.ellipse([x - radius, y - radius, x + radius, y + radius], fill=(*color, strength))

        core = RNG.uniform(1.2, 2.6)
        pd.ellipse([x - core, y - core, x + core, y + core], fill=(*color, RNG.randrange(150, 218)))

    glow = glow.filter(ImageFilter.GaussianBlur(2.6))
    layer.alpha_composite(glow)
    layer.alpha_composite(points)


def draw_location_marker(layer: Image.Image, x: int, y: int) -> None:
    pin = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pin)

    radius = 38
    center_y = y - 50
    deep_green = (8, 86, 42)
    rim = (226, 248, 214)
    highlight = (237, 255, 218)

    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([x - 48, center_y - 36, x + 48, center_y + 44], fill=(4, 42, 20, 80))
    sd.polygon(
        [(x, y + 7), (x - 25, center_y + 21), (x + 25, center_y + 21)],
        fill=(4, 42, 20, 80),
    )
    layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))

    pd.polygon(
        [(x, y + 9), (x - 27, center_y + 20), (x + 27, center_y + 20)],
        fill=(*deep_green, 248),
    )
    pd.ellipse(
        [x - radius, center_y - radius, x + radius, center_y + radius],
        fill=(*deep_green, 248),
        outline=(*rim, 216),
        width=5,
    )
    pd.ellipse(
        [x - 16, center_y - 16, x + 16, center_y + 16],
        fill=(*highlight, 246),
    )
    pd.ellipse(
        [x - 7, center_y - 7, x + 7, center_y + 7],
        fill=(22, 114, 56, 245),
    )
    layer.alpha_composite(pin)


def generate() -> None:
    mask = make_land_mask()
    coast = mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dots = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(dots)

    palette = [
        (9, 72, 31),
        (15, 96, 43),
        (35, 128, 58),
        (82, 167, 86),
        (163, 218, 143),
        (232, 251, 218),
    ]

    # Hex-style dot grid for a coherent dotted-land texture.
    step = 12
    row = 0
    for y in range(8, H - 8, step):
        offset = 0 if row % 2 == 0 else step // 2
        for x in range(8 + offset, W - 8, step):
            a = alpha_at(mask, x, y)
            if a < 54:
                continue
            edge = coast.getpixel((x, y))
            # Keep the grid disciplined while allowing a tiny organic drift.
            jx = x + RNG.uniform(-0.55, 0.55)
            jy = y + RNG.uniform(-0.55, 0.55)
            # Subtle tonal variation across land and coastlines.
            light_bias = (
                0.10
                + 0.10 * math.sin((jx / W) * math.pi * 2.5 + 0.5) ** 2
                + 0.08 * math.cos((jy / H) * math.pi * 2.8) ** 2
                + 0.12 * (a / 255)
                + 0.12 * min(1, edge / 128)
            )
            roll = RNG.random()
            if roll < 0.62:
                color = palette[1]
                alpha = 148
                r = RNG.uniform(1.45, 2.15)
            elif roll < 0.84:
                color = palette[2]
                alpha = 160
                r = RNG.uniform(1.55, 2.28)
            elif roll < 0.965:
                color = palette[3]
                alpha = 166
                r = RNG.uniform(1.65, 2.35)
            elif roll < 0.997:
                color = palette[4]
                alpha = 170
                r = RNG.uniform(1.7, 2.48)
            else:
                color = palette[3]
                alpha = 178
                r = RNG.uniform(1.8, 2.55)
            alpha = min(214, int(alpha + 32 * light_bias))
            d.ellipse([jx - r, jy - r, jx + r, jy + r], fill=(*color, alpha))
        row += 1

    # A dedicated coast layer gives the map a clearer silhouette while remaining
    # a dot matrix rather than a drawn outline.
    for y in range(6, H - 6, 7):
        for x in range(6, W - 6, 7):
            edge = coast.getpixel((x, y))
            if edge < 42 or alpha_at(mask, x, y) < 72 or RNG.random() < 0.58:
                continue
            r = RNG.uniform(0.75, 1.35)
            jx = x + RNG.uniform(-0.45, 0.45)
            jy = y + RNG.uniform(-0.45, 0.45)
            col = RNG.choice([(139, 207, 119), (69, 157, 75), (42, 132, 58)])
            d.ellipse([jx - r, jy - r, jx + r, jy + r], fill=(*col, RNG.randrange(128, 190)))

    out.alpha_composite(dots)
    add_land_sparkles(out, mask)

    for lon, lat in [(-118.2437, 34.0522), (113.2644, 23.1291)]:
        x, y = geo_project((lon, lat))
        draw_location_marker(out, x, y)

    # Trim the invisible padding only a little; keep wide-map proportions for the layout.
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, optimize=True)

    preview_bg = Image.new("RGBA", (W, H), (245, 250, 243, 255))
    preview_bg.alpha_composite(out)
    preview_bg.save(PREVIEW, optimize=True)
    print(f"wrote {OUT} {out.size}")
    print(f"preview {PREVIEW}")


if __name__ == "__main__":
    generate()
