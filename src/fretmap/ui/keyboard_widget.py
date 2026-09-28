"""Виджет для отображения клавиатуры с нотами гаммы."""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ..music.instruments import Instrument
from ..music.theory import Scale, note_name
from ..music.tunings import Tuning
from . import settings as app_settings


COLOR_BG = QColor("#2a2a30")
COLOR_WHITE_KEY = QColor("#e6e6e8")
COLOR_WHITE_KEY_BORDER = QColor("#9a9aa2")
COLOR_BLACK_KEY = QColor("#1a1a1e")
COLOR_BLACK_KEY_BORDER = QColor("#000000")
COLOR_NOTE_TEXT = QColor("#ffffff")
COLOR_OCTAVE_LABEL = QColor("#9a9aa2")


BLACK_PITCH_CLASSES = {1, 3, 6, 8, 10}

MAX_BOARD_W = 1350
MAX_BOARD_H = 240


class KeyboardWidget(QWidget):
    """Клавиатура с нотами выбранной гаммы."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(600, 220)

        self._instrument: Instrument | None = None
        self._tuning: Tuning | None = None
        self._scale: Scale | None = None
        self._show_degrees: bool = False
        self._show_full_range: bool = False

    def set_data(
        self,
        instrument: Instrument,
        tuning: Tuning,
        scale: Scale,
        show_degrees: bool = False,
        show_full_range: bool = False,
    ) -> None:
        self._instrument = instrument
        self._tuning = tuning
        self._scale = scale
        self._show_degrees = show_degrees
        self._show_full_range = show_full_range
        self.update()

    def _effective_range(self) -> tuple[int, int] | None:
        if self._instrument is None or self._instrument.midi_range is None:
            return None
        low, high = self._instrument.midi_range
        if self._show_full_range:
            return low, high
        root = self._scale.root_midi if self._scale else 60
        c_below = (root // 12) * 12
        c_low = max(c_below, low)
        c_high = c_low + 11
        if c_high > high:
            c_high = high
            c_low = c_high - 11
        return c_low, c_high

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), COLOR_BG)

        if not (self._instrument and self._scale):
            return

        note_color = QColor(app_settings.get_note_color())
        tonic_color = QColor(app_settings.get_tonic_color())
        user_scale = app_settings.get_note_scale()

        rng = self._effective_range()
        if rng is None:
            painter.end()
            return
        low_midi, high_midi = rng

        white_pcs = {0, 2, 4, 5, 7, 9, 11}
        while low_midi <= high_midi and (low_midi % 12) not in white_pcs:
            low_midi += 1
        while high_midi >= low_midi and (high_midi % 12) not in white_pcs:
            high_midi -= 1

        white_notes = [m for m in range(low_midi, high_midi + 1) if (m % 12) in white_pcs]
        n_white = len(white_notes)
        if n_white == 0:
            painter.end()
            return

        margin_top = 20
        margin_bottom = 30
        margin_left = 20
        margin_right = 20

        inner_w = self.width() - margin_left - margin_right
        inner_h = self.height() - margin_top - margin_bottom

        if not self._show_full_range:
            max_one_octave_w = 500
            inner_w = min(inner_w, max_one_octave_w)

        total_w = min(inner_w, MAX_BOARD_W)
        total_h = min(inner_h, MAX_BOARD_H)

        offset_x = margin_left + (self.width() - margin_left - margin_right - total_w) / 2
        offset_y = margin_top + (self.height() - margin_top - margin_bottom - total_h) / 2

        painter.translate(offset_x, offset_y)

        white_w = total_w / n_white
        black_w = white_w * 0.6
        black_h = total_h * 0.62

        for i, _midi in enumerate(white_notes):
            x = i * white_w
            painter.setBrush(QBrush(COLOR_WHITE_KEY))
            painter.setPen(QPen(COLOR_WHITE_KEY_BORDER, 1))
            painter.drawRect(QRectF(x, 0, white_w, total_h))

        for i, midi in enumerate(white_notes):
            next_midi = midi + 1
            if next_midi % 12 in BLACK_PITCH_CLASSES and next_midi <= high_midi:
                x_center = (i + 1) * white_w
                x0 = x_center - black_w / 2
                painter.setBrush(QBrush(COLOR_BLACK_KEY))
                painter.setPen(QPen(COLOR_BLACK_KEY_BORDER, 1))
                painter.drawRect(QRectF(x0, 0, black_w, black_h))

        font_oct = QFont()
        font_oct.setPointSize(8)
        painter.setFont(font_oct)
        painter.setPen(COLOR_OCTAVE_LABEL)
        for i, midi in enumerate(white_notes):
            if midi % 12 == 0:
                octave = midi // 12 - 1
                x = i * white_w
                painter.drawText(
                    QRectF(x, total_h - 16, white_w, 14),
                    Qt.AlignmentFlag.AlignCenter,
                    f"C{octave}",
                )

        note_radius = min(white_w * 0.35, total_h * 0.09)
        note_radius = max(note_radius, 6) * user_scale

        root_pc = self._scale.root_midi % 12

        white_index = {midi: i for i, midi in enumerate(white_notes)}
        for midi, i in white_index.items():
            if not self._scale.contains(midi):
                continue
            x_center = (i + 0.5) * white_w
            y_center = total_h * 0.78
            self._draw_note_circle(
                painter, x_center, y_center, note_radius, midi, root_pc,
                note_color, tonic_color,
            )

        for i, midi in enumerate(white_notes):
            next_midi = midi + 1
            if next_midi % 12 in BLACK_PITCH_CLASSES and next_midi <= high_midi:
                if not self._scale.contains(next_midi):
                    continue
                x_center = (i + 1) * white_w
                y_center = black_h * 0.6
                self._draw_note_circle(
                    painter, x_center, y_center, note_radius * 0.85,
                    next_midi, root_pc, note_color, tonic_color,
                )

        painter.end()

    def _draw_note_circle(
        self, painter, cx, cy, radius, midi, root_pc,
        note_color: QColor, tonic_color: QColor,
    ) -> None:
        is_root = (midi % 12) == root_pc
        fill = tonic_color if is_root else note_color

        painter.setBrush(QBrush(fill))
        painter.setPen(QPen(COLOR_BG, 1))
        painter.drawEllipse(QPointF(cx, cy), radius, radius)

        if self._show_degrees:
            deg = self._scale.degree(midi)
            label = str(deg) if deg else "?"
        else:
            label = note_name(midi, self._scale.prefer_flats)

        font = QFont()
        if radius >= 9:
            font.setPointSize(9)
        elif radius >= 6:
            font.setPointSize(7)
        else:
            font.setPointSize(5)
        font.setBold(True)
        painter.setFont(font)

        painter.setPen(COLOR_NOTE_TEXT)
        painter.drawText(
            QRectF(cx - radius, cy - radius, radius * 2, radius * 2),
            Qt.AlignmentFlag.AlignCenter,
            label,
        )