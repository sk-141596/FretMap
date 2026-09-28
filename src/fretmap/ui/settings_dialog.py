"""Диалог настроек с явными кнопками Применить / ОК / Отмена / Сбросить."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from . import settings
from .settings import (
    DEFAULT_ACCENT,
    DEFAULT_NOTE_COLOR,
    DEFAULT_TONIC_COLOR,
)
from .theme import THEMES


class SettingsDialog(QDialog):
    """Диалог настроек приложения."""

    applied = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setMinimumWidth(480)

        # Снимок текущих значений — для отката по «Отмена»
        self._snapshot = {
            "theme": settings.get_theme(),
            "accent": settings.get_accent(),
            "note_color": settings.get_note_color(),
            "tonic_color": settings.get_tonic_color(),
            "font_size": settings.get_font_size(),
            "note_scale": settings.get_note_scale(),
        }

        self._accent_color: str = self._snapshot["accent"] or DEFAULT_ACCENT
        self._note_color: str = self._snapshot["note_color"] or DEFAULT_NOTE_COLOR
        self._tonic_color: str = self._snapshot["tonic_color"] or DEFAULT_TONIC_COLOR

        self._build_ui()
        self._load_current()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        # Тема
        self.theme_combo = QComboBox()
        for key in THEMES:
            self.theme_combo.addItem(key, key)
        form.addRow("Тема:", self.theme_combo)

        # Акцент интерфейса
        accent_row = QHBoxLayout()
        self.accent_preview = QLabel()
        self.accent_preview.setFixedSize(40, 22)
        accent_row.addWidget(self.accent_preview)

        self.accent_btn = QPushButton("Выбрать цвет…")
        self.accent_btn.clicked.connect(self._pick_accent)
        accent_row.addWidget(self.accent_btn)

        self.accent_reset_btn = QPushButton("Сбросить")
        self.accent_reset_btn.clicked.connect(self._reset_accent)
        accent_row.addWidget(self.accent_reset_btn)

        accent_row.addStretch(1)
        form.addRow("Акцент интерфейса:", accent_row)

        # Цвет нот на грифе
        note_row = QHBoxLayout()
        self.note_preview = QLabel()
        self.note_preview.setFixedSize(40, 22)
        note_row.addWidget(self.note_preview)

        self.note_btn = QPushButton("Выбрать цвет…")
        self.note_btn.clicked.connect(self._pick_note_color)
        note_row.addWidget(self.note_btn)

        self.note_reset_btn = QPushButton("Сбросить")
        self.note_reset_btn.clicked.connect(self._reset_note_color)
        note_row.addWidget(self.note_reset_btn)

        note_row.addStretch(1)
        form.addRow("Цвет нот:", note_row)

        # Цвет тоники
        tonic_row = QHBoxLayout()
        self.tonic_preview = QLabel()
        self.tonic_preview.setFixedSize(40, 22)
        tonic_row.addWidget(self.tonic_preview)

        self.tonic_btn = QPushButton("Выбрать цвет…")
        self.tonic_btn.clicked.connect(self._pick_tonic_color)
        tonic_row.addWidget(self.tonic_btn)

        self.tonic_reset_btn = QPushButton("Сбросить")
        self.tonic_reset_btn.clicked.connect(self._reset_tonic_color)
        tonic_row.addWidget(self.tonic_reset_btn)

        tonic_row.addStretch(1)
        form.addRow("Цвет тоники:", tonic_row)

        # Размер шрифта
        font_row = QHBoxLayout()
        self.font_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_slider.setRange(8, 14)
        self.font_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.font_slider.setTickInterval(1)
        self.font_slider.valueChanged.connect(self._on_slider_changed)
        font_row.addWidget(self.font_slider)
        self.font_value = QLabel("10 pt")
        self.font_value.setMinimumWidth(50)
        font_row.addWidget(self.font_value)
        form.addRow("Размер шрифта:", font_row)

        # Размер нот
        scale_row = QHBoxLayout()
        self.note_slider = QSlider(Qt.Orientation.Horizontal)
        self.note_slider.setRange(70, 140)
        self.note_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.note_slider.setTickInterval(10)
        self.note_slider.valueChanged.connect(self._on_slider_changed)
        scale_row.addWidget(self.note_slider)
        self.note_value = QLabel("×1.0")
        self.note_value.setMinimumWidth(50)
        scale_row.addWidget(self.note_value)
        form.addRow("Размер нот:", scale_row)

        root.addLayout(form)
        root.addStretch(1)

        btns = QHBoxLayout()

        self.reset_btn = QPushButton("Сбросить всё")
        self.reset_btn.setToolTip("Вернуть все настройки по умолчанию")
        self.reset_btn.clicked.connect(self._reset_defaults)
        btns.addWidget(self.reset_btn)

        btns.addStretch(1)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self._on_cancel)
        btns.addWidget(self.cancel_btn)

        self.apply_btn = QPushButton("Применить")
        self.apply_btn.clicked.connect(self._on_apply)
        btns.addWidget(self.apply_btn)

        self.ok_btn = QPushButton("ОК")
        self.ok_btn.setObjectName("primary")
        self.ok_btn.clicked.connect(self._on_ok)
        btns.addWidget(self.ok_btn)

        root.addLayout(btns)

        self._update_accent_preview()
        self._update_note_preview()
        self._update_tonic_preview()

    # ---------- заполнение ----------

    def _load_current(self) -> None:
        idx = self.theme_combo.findData(self._snapshot["theme"])
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        self.font_slider.blockSignals(True)
        self.font_slider.setValue(self._snapshot["font_size"])
        self.font_value.setText(f"{self._snapshot['font_size']} pt")
        self.font_slider.blockSignals(False)

        note_scale = self._snapshot["note_scale"]
        self.note_slider.blockSignals(True)
        self.note_slider.setValue(int(note_scale * 100))
        self.note_value.setText(f"×{note_scale:.1f}")
        self.note_slider.blockSignals(False)

    def _on_slider_changed(self) -> None:
        self.font_value.setText(f"{self.font_slider.value()} pt")
        self.note_value.setText(f"×{self.note_slider.value() / 100:.1f}")

    # ---------- превью ----------

    def _update_accent_preview(self) -> None:
        color = self._accent_color or DEFAULT_ACCENT
        self.accent_preview.setStyleSheet(
            f"background-color: {color};"
            f"border: 1px solid #3d3d46; border-radius: 3px;"
        )

    def _update_note_preview(self) -> None:
        color = self._note_color or DEFAULT_NOTE_COLOR
        self.note_preview.setStyleSheet(
            f"background-color: {color};"
            f"border: 1px solid #3d3d46; border-radius: 11px;"
        )

    def _update_tonic_preview(self) -> None:
        color = self._tonic_color or DEFAULT_TONIC_COLOR
        self.tonic_preview.setStyleSheet(
            f"background-color: {color};"
            f"border: 1px solid #3d3d46; border-radius: 11px;"
        )

    # ---------- выбор цвета ----------

    def _pick_accent(self) -> None:
        initial = QColor(self._accent_color or DEFAULT_ACCENT)
        color = QColorDialog.getColor(initial, self, "Акцент интерфейса")
        if not color.isValid():
            return
        self._accent_color = color.name()
        self._update_accent_preview()

    def _pick_note_color(self) -> None:
        initial = QColor(self._note_color or DEFAULT_NOTE_COLOR)
        color = QColorDialog.getColor(initial, self, "Цвет нот на грифе")
        if not color.isValid():
            return
        self._note_color = color.name()
        self._update_note_preview()

    def _pick_tonic_color(self) -> None:
        initial = QColor(self._tonic_color or DEFAULT_TONIC_COLOR)
        color = QColorDialog.getColor(initial, self, "Цвет тоники")
        if not color.isValid():
            return
        self._tonic_color = color.name()
        self._update_tonic_preview()

    # ---------- сброс отдельных ----------

    def _reset_accent(self) -> None:
        self._accent_color = DEFAULT_ACCENT
        self._update_accent_preview()

    def _reset_note_color(self) -> None:
        self._note_color = DEFAULT_NOTE_COLOR
        self._update_note_preview()

    def _reset_tonic_color(self) -> None:
        self._tonic_color = DEFAULT_TONIC_COLOR
        self._update_tonic_preview()

    # ---------- кнопки ----------

    def _commit_to_settings(self) -> None:
        settings.set_theme(self.theme_combo.currentData())
        settings.set_accent(self._accent_color)
        settings.set_note_color(self._note_color)
        settings.set_tonic_color(self._tonic_color)
        settings.set_font_size(self.font_slider.value())
        settings.set_note_scale(self.note_slider.value() / 100.0)

    def _on_apply(self) -> None:
        self._commit_to_settings()
        self.applied.emit()

    def _on_ok(self) -> None:
        self._commit_to_settings()
        self.applied.emit()
        self.accept()

    def _on_cancel(self) -> None:
        settings.set_theme(self._snapshot["theme"])
        settings.set_accent(self._snapshot["accent"])
        settings.set_note_color(self._snapshot["note_color"])
        settings.set_tonic_color(self._snapshot["tonic_color"])
        settings.set_font_size(self._snapshot["font_size"])
        settings.set_note_scale(self._snapshot["note_scale"])
        self.applied.emit()
        self.reject()

    def _reset_defaults(self) -> None:
        idx = self.theme_combo.findData("nord")
        if idx >= 0:
            self.theme_combo.setCurrentIndex(idx)

        self.font_slider.setValue(10)
        self.note_slider.setValue(100)
        self._accent_color = DEFAULT_ACCENT
        self._note_color = DEFAULT_NOTE_COLOR
        self._tonic_color = DEFAULT_TONIC_COLOR

        self._update_accent_preview()
        self._update_note_preview()
        self._update_tonic_preview()