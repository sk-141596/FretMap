"""Сгенерировать icon.ico для приложения.

Использование:
    python scripts/generate_icon.py
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw


BG = (46, 52, 64)          # #2e3440 — nord bg
SURFACE = (59, 66, 82)     # #3b4252 — nord surface
ACCENT = (58, 138, 138)    # #3a8a8a — дефолтный бирюзовый акцент
TEXT = (236, 239, 244)     # #eceff4 — nord text


SIZES = [16, 24, 32, 48, 64, 128, 256]


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), BG + (255,))
    draw = ImageDraw.Draw(img)

    # Скруглённый фон
    radius = max(2, size // 8)
    draw.rounded_rectangle(
        [(0, 0), (size - 1, size - 1)],
        radius=radius,
        fill=BG + (255,),
    )

    # Кольцо-акцент по краю
    ring_w = max(1, size // 24)
    draw.rounded_rectangle(
        [(ring_w // 2, ring_w // 2), (size - 1 - ring_w // 2, size - 1 - ring_w // 2)],
        radius=radius,
        outline=ACCENT + (255,),
        width=ring_w,
    )

    # Внутри — три «струны» и три ноты на них
    padding = max(2, size // 5)
    inner_w = size - 2 * padding
    inner_h = size - 2 * padding

    # Струны (горизонтальные линии)
    n_strings = 3
    line_w = max(1, size // 40)
    strings_y = [
        padding + int(inner_h * (i + 1) / (n_strings + 1))
        for i in range(n_strings)
    ]
    for y in strings_y:
        draw.line(
            [(padding, y), (padding + inner_w, y)],
            fill=TEXT + (140,),
            width=line_w,
        )

    # Ноты на струнах — кружки
    note_r = max(2, size // 10)
    note_xs = [
        padding + int(inner_w * 0.25),
        padding + int(inner_w * 0.5),
        padding + int(inner_w * 0.75),
    ]
    for x, y in zip(note_xs, strings_y):
        # Сам кружок ноты
        draw.ellipse(
            [(x - note_r, y - note_r), (x + note_r, y + note_r)],
            fill=ACCENT + (255,),
        )
        # Обводка
        draw.ellipse(
            [(x - note_r, y - note_r), (x + note_r, y + note_r)],
            outline=BG + (255,),
            width=max(1, size // 64),
        )

    # Тонкий блик сверху
    if size >= 32:
        draw.ellipse(
            [
                (size // 4, size // 6),
                (size // 4 + size // 8, size // 6 + size // 12),
            ],
            fill=(255, 255, 255, 30),
        )

    return img


def main() -> None:
    output = Path(__file__).parent.parent / "src" / "fretmap" / "ui" / "icon.ico"
    output.parent.mkdir(parents=True, exist_ok=True)

    images = [draw_icon(s) for s in SIZES]
    images[0].save(
        output,
        format="ICO",
        sizes=[(s, s) for s in SIZES],
        append_images=images[1:],
    )
    print(f"OK: {output}")


if __name__ == "__main__":
    main()