"""Виджет для отображения грифовой диаграммы с нотами гаммы.

Рисует гриф «как настоящий»: с головой, колками, деревянной накладкой
с текстурой, металлическими ладами и экспоненциальным уменьшением
расстояния между ладами.
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import QWidget

from ..music.instruments import Instrument
from ..music.theory import Scale, note_name, note_name_with_octave
from ..music.tunings import Tuning
from . import settings as app_settings


WOOD_PALETTES: dict[str, dict] = {
    "rosewood": {
        "light": QColor("#7a4f2e"),
        "dark": QColor("#5a3820"),
        "grain": QColor(40, 20, 10, 70),
        "grain_count": 14,
        "grain_wobble": 1.5,
    },
    "ebony": {
        "light": QColor("#4a3222"),
        "dark": QColor("#2e1e14"),
        "grain": QColor(15, 8, 4, 60),
        "grain_count": 9,
        "grain_wobble": 0.8,
    },
    "maple": {
        "light": QColor("#b08858"),
        "dark": QColor("#8a6838"),
        "grain": QColor(80, 50, 20, 55),
        "grain_count": 18,
        "grain_wobble": 2.2,
    },
    "walnut": {
        "light": QColor("#6a4830"),
        "dark": QColor("#4a3020"),
        "grain": QColor(30, 15, 8, 90),
        "grain_count": 11,
        "grain_wobble": 3.0,
    },
}


COLOR_BG = QColor("#2a2a30")
COLOR_HEAD = QColor("#5a3a24")
COLOR_HEAD_EDGE = QColor("#2a1a10")
COLOR_BOARD_EDGE = QColor("#2a1a10")
COLOR_PEG = QColor("#d4b878")
COLOR_PEG_INNER = QColor("#8a6a30")
COLOR_PEG_BORDER = QColor("#5a4020")
COLOR_STRING = QColor("#d8d8dc")
COLOR_FRET = QColor("#c8c8d0")
COLOR_FRET_NUMBER = QColor("#9a9aa2")
COLOR_FRET_MARKER = QColor("#e6e6e8")
COLOR_NOTE_TEXT = QColor("#e6e6e8")
COLOR_NUT = QColor("#e8e0d0")
COLOR_STRING_LABEL = QColor("#2a1a10")


FRET_MARKERS = {3, 5, 7, 9, 12, 15, 17, 19, 21, 24}
DOUBLE_MARKER_FRETS = {12, 24}

MAX_BOARD_W = 1400
MAX_BOARD_H = 250

NOTE_RADIUS_MIN = 5.0
NOTE_RADIUS_MAX = 16.0

HEAD_WIDENING = 1.30


def _polygon_to_path(poly: QPolygonF) -> QPainterPath:
    path = QPainterPath()
    if poly.isEmpty():
        return path
    path.moveTo(poly.at(0))
    for i in range(1, poly.count()):
        path.lineTo(poly.at(i))
    path.closeSubpath()
    return path


class FretboardWidget(QWidget):
    """Гриф с нотами выбранной гаммы."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(1000, 280)

        self._instrument: Instrument | None = None
        self._tuning: Tuning | None = None
        self._scale: Scale | None = None
        self._show_degrees: bool = False
        self._max_fret: int = 12
        self._wood_style: str = "rosewood"

    def set_data(
        self,
        instrument: Instrument,
        tuning: Tuning,
        scale: Scale,
        max_fret: int = 12,
        show_degrees: bool = False,
        wood_style: str = "rosewood",
    ) -> None:
        self._instrument = instrument
        self._tuning = tuning
        self._scale = scale
        self._max_fret = max(1, max_fret)
        self._show_degrees = show_degrees
        self._wood_style = wood_style
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), COLOR_BG)

        if not (self._instrument and self._tuning and self._scale):
            return

        # Читаем пользовательские цвета
        note_color = QColor(app_settings.get_note_color())
        tonic_color = QColor(app_settings.get_tonic_color())
        user_scale = app_settings.get_note_scale()

        wood = WOOD_PALETTES.get(self._wood_style, WOOD_PALETTES["rosewood"])
        strings = self._tuning.strings_midi
        n_strings = len(strings)
        n_frets = self._max_fret

        margin_top = 50
        margin_bottom = 35
        margin_left = 20
        margin_right = 15

        inner_w = self.width() - margin_left - margin_right
        inner_h = self.height() - margin_top - margin_bottom

        total_w = min(inner_w, MAX_BOARD_W)
        total_h = min(inner_h, MAX_BOARD_H)

        offset_x = margin_left + (inner_w - total_w) / 2
        offset_y = margin_top + (inner_h - total_h) / 2

        painter.translate(offset_x, offset_y)

        head_ratio = 0.28
        head_w = total_w * head_ratio
        board_w = total_w - head_w

        right_padding = board_w * 0.06
        usable_w = board_w - right_padding

        y_center = total_h / 2
        spread_at_nut = total_h * 0.72
        spread_at_end = total_h * 0.78
        board_pad_at_nut = spread_at_nut * 0.16
        board_pad_at_end = spread_at_end * 0.16
        board_full_at_nut = spread_at_nut + 2 * board_pad_at_nut
        head_max_spread = board_full_at_nut * HEAD_WIDENING

        if n_frets > 0:
            L = usable_w / (1 - 2 ** (-n_frets / 12))
        else:
            L = usable_w

        def fret_x(fret: int) -> float:
            if fret == 0:
                return 0.0
            return L * (1 - 2 ** (-fret / 12))

        def string_spread_at(x_local: float) -> float:
            t = x_local / usable_w if usable_w > 0 else 0.0
            return spread_at_nut + (spread_at_end - spread_at_nut) * t

        def board_pad_at(x_local: float) -> float:
            t = x_local / usable_w if usable_w > 0 else 0.0
            return board_pad_at_nut + (board_pad_at_end - board_pad_at_nut) * t

        def string_y(idx: int, x_local: float) -> float:
            if n_strings == 1:
                return y_center
            spread = string_spread_at(x_local)
            pos = (n_strings - 1 - idx) / (n_strings - 1)
            y_top = y_center - spread / 2
            return y_top + pos * spread

        head_x0 = 0
        head_x1 = head_w
        nut_x = head_x1
        end_local = fret_x(n_frets)
        end_x = nut_x + end_local

        def head_spread_at_x(x: float) -> float:
            t = (head_x1 - x) / head_w if head_w > 0 else 0.0
            t = max(0.0, min(1.0, t))
            return board_full_at_nut + (head_max_spread - board_full_at_nut) * t

        peg_r = board_full_at_nut * 0.10
        peg_positions = self._compute_peg_positions(
            n_strings=n_strings,
            head_x0=head_x0,
            head_x1=head_x1,
            head_w=head_w,
            y_center=y_center,
            head_spread_at_x=head_spread_at_x,
            peg_radius=peg_r,
        )

        # --- Голова ---
        head_poly = self._build_head_profile(
            head_x0=head_x0,
            head_x1=head_x1,
            y_center=y_center,
            board_full_at_nut=board_full_at_nut,
            head_max_spread=head_max_spread,
        )
        painter.setBrush(QBrush(COLOR_HEAD))
        painter.setPen(QPen(COLOR_HEAD_EDGE, 2))
        painter.drawPolygon(head_poly)

        # --- Накладка ---
        top_nut_y = y_center - spread_at_nut / 2 - board_pad_at_nut
        top_end_y = y_center - spread_at_end / 2 - board_pad_at_end
        bot_nut_y = y_center + spread_at_nut / 2 + board_pad_at_nut
        bot_end_y = y_center + spread_at_end / 2 + board_pad_at_end

        board_poly = QPolygonF([
            QPointF(nut_x, top_nut_y),
            QPointF(end_x, top_end_y),
            QPointF(end_x, bot_end_y),
            QPointF(nut_x, bot_nut_y),
        ])

        grad = QLinearGradient(nut_x, 0, end_x, 0)
        grad.setColorAt(0.0, wood["light"])
        grad.setColorAt(1.0, wood["dark"])

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(COLOR_BOARD_EDGE, 1))
        painter.drawPolygon(board_poly)

        painter.save()
        painter.setClipPath(_polygon_to_path(board_poly))
        painter.setPen(QPen(wood["grain"], 1))
        n_grains = wood["grain_count"]
        wobble_scale = wood["grain_wobble"]
        for k in range(1, n_grains):
            frac = k / n_grains
            y_start = top_nut_y + frac * (bot_nut_y - top_nut_y)
            y_end = top_end_y + frac * (bot_end_y - top_end_y)
            wobble = ((k * 7) % 5 - 2) * wobble_scale
            mid_x = (nut_x + end_x) / 2
            mid_y = (y_start + y_end) / 2 + wobble
            path = QPainterPath(QPointF(nut_x, y_start))
            path.quadTo(QPointF(mid_x, mid_y), QPointF(end_x, y_end))
            painter.drawPath(path)
        painter.restore()

        # --- Порожек ---
        painter.setPen(QPen(COLOR_NUT, 4))
        painter.drawLine(QPointF(nut_x, top_nut_y), QPointF(nut_x, bot_nut_y))

        # --- Лады ---
        painter.setPen(QPen(COLOR_FRET, 2))
        for fret in range(1, n_frets + 1):
            x_local = fret_x(fret)
            x = nut_x + x_local
            pad = board_pad_at(x_local)
            spread = string_spread_at(x_local)
            painter.drawLine(
                QPointF(x, y_center - spread / 2 - pad),
                QPointF(x, y_center + spread / 2 + pad),
            )

        # --- Маркеры ---
        painter.setBrush(QBrush(COLOR_FRET_MARKER))
        painter.setPen(Qt.PenStyle.NoPen)
        marker_radius = max(2.0, total_h * 0.015)
        for fret in sorted(FRET_MARKERS):
            if fret > n_frets:
                continue
            x_a = fret_x(fret - 1)
            x_b = fret_x(fret)
            x_local = (x_a + x_b) / 2
            x = nut_x + x_local
            if fret in DOUBLE_MARKER_FRETS:
                spread = string_spread_at(x_local)
                offset = spread * 0.22
                painter.drawEllipse(QPointF(x, y_center - offset), marker_radius, marker_radius)
                painter.drawEllipse(QPointF(x, y_center + offset), marker_radius, marker_radius)
            else:
                painter.drawEllipse(QPointF(x, y_center), marker_radius, marker_radius)

        # --- Струны ---
        for idx in range(n_strings):
            thickness = 1.0 + (n_strings - 1 - idx) * 0.35
            painter.setPen(QPen(COLOR_STRING, thickness))
            px, py = peg_positions[idx]
            y_nut = string_y(idx, 0)
            painter.drawLine(QPointF(px, py), QPointF(nut_x, y_nut))
            y_end = string_y(idx, end_local)
            painter.drawLine(QPointF(nut_x, y_nut), QPointF(end_x, y_end))

        # --- Колки ---
        for idx in range(n_strings):
            px, py = peg_positions[idx]
            painter.setBrush(QBrush(COLOR_PEG))
            painter.setPen(QPen(COLOR_PEG_BORDER, 1))
            painter.drawEllipse(QPointF(px, py), peg_r, peg_r)
            painter.setBrush(QBrush(COLOR_PEG_INNER))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), peg_r * 0.45, peg_r * 0.45)

        # --- Подписи струн ---
        font_str = QFont()
        font_str.setPointSize(8)
        font_str.setBold(True)
        painter.setFont(font_str)
        painter.setPen(COLOR_STRING_LABEL)
        for idx, midi in enumerate(strings):
            px, py = peg_positions[idx]
            label = note_name_with_octave(midi, self._scale.prefer_flats)
            painter.drawText(
                QRectF(px - head_w * 0.35, py - 18, head_w * 0.7, 14),
                Qt.AlignmentFlag.AlignCenter,
                label,
            )

        # --- Номера ладов ---
        font_fret = QFont()
        font_fret.setPointSize(8)
        painter.setFont(font_fret)
        painter.setPen(COLOR_FRET_NUMBER)
        for fret in range(1, n_frets + 1):
            x_a = fret_x(fret - 1)
            x_b = fret_x(fret)
            x_mid = nut_x + (x_a + x_b) / 2
            if x_b - x_a >= 12:
                painter.drawText(
                    QRectF(x_mid - 15, bot_end_y + 6, 30, 18),
                    Qt.AlignmentFlag.AlignCenter,
                    str(fret),
                )

        # --- Кружки с нотами ---
        note_radius = self._compute_note_radius(
            total_h=total_h,
            n_strings=n_strings,
            spread_at_nut=spread_at_nut,
            fret_x=fret_x,
        )
        note_radius *= user_scale

        font_note = QFont()
        font_pt = max(6, int(note_radius * 0.85))
        font_note.setPointSize(font_pt)
        font_note.setBold(True)
        painter.setFont(font_note)

        root_pc = self._scale.root_midi % 12
        for string_idx, open_midi in enumerate(strings):
            for fret in range(0, n_frets + 1):
                midi = open_midi + fret
                if not self._scale.contains(midi):
                    continue
                if fret == 0:
                    x_local = fret_x(0)
                    x = nut_x + x_local
                    y = string_y(string_idx, x_local)
                else:
                    x_a = fret_x(fret - 1)
                    x_b = fret_x(fret)
                    x_local = (x_a + x_b) / 2
                    x = nut_x + x_local
                    y = string_y(string_idx, x_local)
                if fret == 0:
                    fret_w = fret_x(1) - fret_x(0)
                else:
                    fret_w = fret_x(fret) - fret_x(fret - 1)
                r = min(note_radius, fret_w * 0.42)
                is_root = (midi % 12) == root_pc
                fill = tonic_color if is_root else note_color
                painter.setBrush(QBrush(fill))
                painter.setPen(QPen(COLOR_BG, 1))
                painter.drawEllipse(QPointF(x, y), r, r)
                if r >= 4.5:
                    if self._show_degrees:
                        deg = self._scale.degree(midi)
                        label = str(deg) if deg else "?"
                    else:
                        label = note_name(midi, self._scale.prefer_flats)
                    painter.setPen(COLOR_NOTE_TEXT)
                    painter.drawText(
                        QRectF(x - r, y - r, r * 2, r * 2),
                        Qt.AlignmentFlag.AlignCenter,
                        label,
                    )
        painter.end()

    def _compute_note_radius(self, total_h, n_strings, spread_at_nut, fret_x):
        if n_strings > 1:
            string_gap = spread_at_nut / (n_strings - 1)
        else:
            string_gap = spread_at_nut
        first_fret_w = fret_x(1) - fret_x(0)
        candidates = [string_gap * 0.40, first_fret_w * 0.42, total_h * 0.10]
        r = min(candidates)
        r = max(NOTE_RADIUS_MIN, min(NOTE_RADIUS_MAX, r))
        return r

    def _build_head_profile(self, head_x0, head_x1, y_center, board_full_at_nut, head_max_spread):
        w = head_x1 - head_x0
        nut_half = board_full_at_nut / 2
        mid_half = head_max_spread / 2
        points = [
            QPointF(head_x0 + w * 0.03, y_center - mid_half * 0.85),
            QPointF(head_x0 + w * 0.20, y_center - mid_half),
            QPointF(head_x0 + w * 0.55, y_center - mid_half),
            QPointF(head_x0 + w * 0.88, y_center - (mid_half + nut_half) / 2),
            QPointF(head_x1, y_center - nut_half),
            QPointF(head_x1, y_center + nut_half),
            QPointF(head_x0 + w * 0.88, y_center + (mid_half + nut_half) / 2),
            QPointF(head_x0 + w * 0.55, y_center + mid_half),
            QPointF(head_x0 + w * 0.20, y_center + mid_half),
            QPointF(head_x0 + w * 0.03, y_center + mid_half * 0.85),
        ]
        return QPolygonF(points)

    def _compute_peg_positions(self, n_strings, head_x0, head_x1, head_w, y_center, head_spread_at_x, peg_radius):
        positions = [None] * n_strings
        margin_x = peg_radius * 1.5 + head_w * 0.02
        x_near = head_x1 - margin_x - head_w * 0.04
        x_far_base = head_x0 + margin_x
        x_far = x_far_base + peg_radius * 1.2 + head_w * 0.05
        x_mid = (x_near + x_far) / 2
        n_top = (n_strings + 1) // 2
        n_bot = n_strings - n_top

        def xs_for_row(count):
            if count <= 0: return []
            if count == 1: return [x_mid]
            if count == 2: return [x_near, x_far]
            if count == 3: return [x_near, x_mid, x_far]
            result = []
            for i in range(count):
                t = i / (count - 1)
                result.append(x_near + (x_far - x_near) * t)
            return result

        base_margin = peg_radius * 1.2
        tilt = 0.14

        def y_top_at(x):
            spread = head_spread_at_x(x)
            half = spread / 2
            t = (head_x1 - x) / head_w if head_w > 0 else 0.0
            t = max(0.0, min(1.0, t))
            extra = half * tilt * t
            return y_center - half + base_margin + extra

        def y_bot_at(x):
            spread = head_spread_at_x(x)
            half = spread / 2
            t = (head_x1 - x) / head_w if head_w > 0 else 0.0
            t = max(0.0, min(1.0, t))
            extra = half * tilt * t
            return y_center + half - base_margin - extra

        top_strings = list(range(n_strings - 1, n_bot - 1, -1))
        top_xs = xs_for_row(n_top)
        for i, sidx in enumerate(top_strings):
            x = top_xs[i]
            positions[sidx] = (x, y_top_at(x))
        bot_strings = list(range(0, n_bot))
        bot_xs = xs_for_row(n_bot)
        for i, sidx in enumerate(bot_strings):
            x = bot_xs[i]
            positions[sidx] = (x, y_bot_at(x))
        for i in range(n_strings):
            if positions[i] is None:
                positions[i] = (x_mid, y_center)
        return positions