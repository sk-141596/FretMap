"""Карточка одного инструмента."""

from __future__ import annotations

from PySide6.QtCore import QEvent, QMimeData, QPoint, Qt, Signal
from PySide6.QtGui import QColor, QDrag, QFont, QPainter, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..music.instruments import models_for_frets
from ..music.theory import SCALE_DISPLAY_NAMES, Scale, note_name, parse_note
from .cards_container import MIME_TYPE
from .fretboard_widget import FretboardWidget
from .instrument_view import InstrumentView
from .keyboard_widget import KeyboardWidget


ROOT_NOTES = [
    "C", "C#", "Db", "D", "D#", "Eb", "E", "F",
    "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B",
]


class InstrumentCard(QFrame):
    """Карточка с одним инструментом."""

    remove_requested = Signal(object)

    def __init__(self, view: InstrumentView, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._view = view
        self._drag_start_pos: QPoint | None = None

        self.setObjectName("card")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._content_widget: QWidget | None = None
        self._build_ui()
        self._apply_view()

    @property
    def view(self) -> InstrumentView:
        return self._view

    def set_root_note(self, root_name: str) -> None:
        root_midi = parse_note(f"{root_name}4")
        prefer_flats = "b" in root_name
        self._view.scale = Scale(
            root_midi, self._view.scale.scale_name, prefer_flats=prefer_flats
        )
        self._apply_view()

    def set_scale_name(self, scale_name: str) -> None:
        self._view.scale = Scale(
            self._view.scale.root_midi,
            scale_name,
            prefer_flats=self._view.scale.prefer_flats,
        )
        self._apply_view()

    # ---------- UI ----------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(0)

        self.drag_handle = QLabel("⠿")
        self.drag_handle.setFixedWidth(26)
        self.drag_handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drag_handle.setToolTip("Потяните за эту ручку, чтобы изменить порядок")
        self.drag_handle.setCursor(Qt.CursorShape.OpenHandCursor)
        self.drag_handle.setStyleSheet(
            "QLabel {"
            "  color: palette(mid);"
            "  background: transparent;"
            "  padding: 0;"
            "}"
        )
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.drag_handle.setFont(font)
        self.drag_handle.installEventFilter(self)
        header.addWidget(self.drag_handle)

        # Отступ от ручки до заголовка
        header.addSpacing(12)

        self.title_label = QLabel()
        self.title_label.setTextFormat(Qt.TextFormat.PlainText)
        # padding-left даёт видимый зазор слева от текста
        self.title_label.setStyleSheet(
            "font-weight: bold; font-size: 11pt; padding-left: 8px;"
        )
        header.addWidget(self.title_label, stretch=1)

        header.addSpacing(6)

        self.remove_btn = QPushButton("×")
        self.remove_btn.setObjectName("cardClose")
        self.remove_btn.setFixedSize(26, 26)
        self.remove_btn.setToolTip("Удалить инструмент")
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        header.addWidget(self.remove_btn)

        layout.addLayout(header)

        # Параметры
        params = QHBoxLayout()
        params.setSpacing(8)

        self.tuning_label = QLabel("Строй:")
        self.tuning_label.setObjectName("fieldLabel")
        params.addWidget(self.tuning_label)
        self.tuning_combo = QComboBox()
        self.tuning_combo.setMinimumWidth(160)
        self.tuning_combo.currentIndexChanged.connect(self._on_params_changed)
        params.addWidget(self.tuning_combo)

        self.frets_label = QLabel("Ладов:")
        self.frets_label.setObjectName("fieldLabel")
        params.addWidget(self.frets_label)
        self.frets_combo = QComboBox()
        self.frets_combo.setMinimumWidth(110)
        self.frets_combo.currentIndexChanged.connect(self._on_params_changed)
        params.addWidget(self.frets_combo)

        self.root_label = QLabel("Тоника:")
        self.root_label.setObjectName("fieldLabel")
        params.addWidget(self.root_label)
        self.root_combo = QComboBox()
        self.root_combo.addItems(ROOT_NOTES)
        self.root_combo.setMinimumWidth(60)
        self.root_combo.currentIndexChanged.connect(self._on_params_changed)
        params.addWidget(self.root_combo)

        self.scale_label = QLabel("Лад:")
        self.scale_label.setObjectName("fieldLabel")
        params.addWidget(self.scale_label)
        self.scale_combo = QComboBox()
        for key, display in SCALE_DISPLAY_NAMES.items():
            self.scale_combo.addItem(display, key)
        self.scale_combo.setMinimumWidth(160)
        self.scale_combo.currentIndexChanged.connect(self._on_params_changed)
        params.addWidget(self.scale_combo)

        # Полный диапазон — только для клавишных
        self.full_range_cb = QCheckBox("Полный диапазон")
        self.full_range_cb.setToolTip(
            "Показывать весь диапазон инструмента вместо одной октавы"
        )
        self.full_range_cb.toggled.connect(self._on_params_changed)
        params.addWidget(self.full_range_cb)

        params.addStretch(1)

        self.degrees_btn = QPushButton("Ступени")
        self.degrees_btn.setCheckable(True)
        self.degrees_btn.setFixedHeight(26)
        self.degrees_btn.toggled.connect(self._on_params_changed)
        params.addWidget(self.degrees_btn)

        layout.addLayout(params)

        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_container)

    # ---------- заполнение ----------

    def _apply_view(self) -> None:
        v = self._view

        frets = v.effective_fret_count()
        models = models_for_frets(frets)
        if v.instrument.is_stringed:
            if models:
                title = (
                    f"{v.instrument.display_name}  —  "
                    f"{frets} ладов ({models})"
                )
            else:
                title = (
                    f"{v.instrument.display_name}  —  "
                    f"{v.instrument.model_name}  —  "
                    f"{frets} ладов"
                )
        else:
            title = v.instrument.display_name
        self.title_label.setText(title)

        # Строй
        self.tuning_combo.blockSignals(True)
        self.tuning_combo.clear()
        if v.instrument.tunings:
            for t in v.instrument.tunings:
                self.tuning_combo.addItem(t.display_name, t.id)
            idx = self.tuning_combo.findData(v.tuning.id)
            if idx >= 0:
                self.tuning_combo.setCurrentIndex(idx)
            self.tuning_combo.setVisible(True)
            self.tuning_label.setVisible(True)
        else:
            self.tuning_combo.setVisible(False)
            self.tuning_label.setVisible(False)
        self.tuning_combo.blockSignals(False)

        # Лады
        self.frets_combo.blockSignals(True)
        self.frets_combo.clear()
        if v.instrument.is_stringed:
            lo, hi = v.instrument.fret_range
            std = v.instrument.fret_count
            self.frets_combo.addItem(f"Стандарт ({std})", std)
            for n in range(lo, hi + 1):
                if n != std:
                    self.frets_combo.addItem(f"{n}", n)
            target = v.effective_fret_count()
            idx = self.frets_combo.findData(target)
            if idx >= 0:
                self.frets_combo.setCurrentIndex(idx)
            self.frets_combo.setVisible(True)
            self.frets_label.setVisible(True)
        else:
            self.frets_combo.setVisible(False)
            self.frets_label.setVisible(False)
        self.frets_combo.blockSignals(False)

        # Полный диапазон — видим только для клавишных
        is_keyboard = not v.instrument.is_stringed
        self.full_range_cb.blockSignals(True)
        self.full_range_cb.setChecked(v.show_full_range)
        self.full_range_cb.setVisible(is_keyboard)
        self.full_range_cb.blockSignals(False)

        # Тоника
        self.root_combo.blockSignals(True)
        root_name = note_name(v.scale.root_midi, v.scale.prefer_flats)
        idx = self.root_combo.findText(root_name)
        if idx >= 0:
            self.root_combo.setCurrentIndex(idx)
        self.root_combo.blockSignals(False)

        # Лад
        self.scale_combo.blockSignals(True)
        idx = self.scale_combo.findData(v.scale.scale_name)
        if idx >= 0:
            self.scale_combo.setCurrentIndex(idx)
        self.scale_combo.blockSignals(False)

        # Ступени
        self.degrees_btn.blockSignals(True)
        self.degrees_btn.setChecked(v.show_degrees)
        self.degrees_btn.blockSignals(False)

        # Контент
        if v.instrument.is_stringed:
            self._set_fretboard(v)
        else:
            self._set_keyboard(v)

    def _on_params_changed(self) -> None:
        v = self._view

        if v.instrument.tunings:
            tuning_id = self.tuning_combo.currentData()
            for t in v.instrument.tunings:
                if t.id == tuning_id:
                    v.tuning = t
                    break

        if v.instrument.is_stringed:
            sel = self.frets_combo.currentData()
            if sel is not None:
                v.fret_count = sel if sel != v.instrument.fret_count else None

        root_name = self.root_combo.currentText()
        root_midi = parse_note(f"{root_name}4")
        prefer_flats = "b" in root_name
        scale_name = self.scale_combo.currentData()
        v.scale = Scale(root_midi, scale_name, prefer_flats=prefer_flats)

        v.show_degrees = self.degrees_btn.isChecked()
        v.show_full_range = self.full_range_cb.isChecked()
        self._apply_view()

    def _clear_content(self) -> None:
        if self._content_widget is not None:
            self.content_layout.removeWidget(self._content_widget)
            self._content_widget.deleteLater()
            self._content_widget = None

    def _set_fretboard(self, v: InstrumentView) -> None:
        self._clear_content()
        widget = FretboardWidget()
        widget.setMinimumHeight(240)
        widget.set_data(
            instrument=v.instrument,
            tuning=v.tuning,
            scale=v.scale,
            max_fret=v.effective_fret_count(),
            show_degrees=v.show_degrees,
            wood_style=v.instrument.wood_style,
        )
        self.content_layout.addWidget(widget)
        self._content_widget = widget

    def _set_keyboard(self, v: InstrumentView) -> None:
        self._clear_content()
        widget = KeyboardWidget()
        widget.setMinimumHeight(190)
        widget.set_data(
            instrument=v.instrument,
            tuning=v.tuning,
            scale=v.scale,
            show_degrees=v.show_degrees,
            show_full_range=v.show_full_range,
        )
        self.content_layout.addWidget(widget)
        self._content_widget = widget

    # ---------- drag через ручку ----------

    def eventFilter(self, obj, event) -> bool:
        if obj is self.drag_handle:
            if event.type() == QEvent.Type.MouseButtonPress:
                if event.button() == Qt.MouseButton.LeftButton:
                    self._drag_start_pos = event.position().toPoint()
                    return False
            if event.type() == QEvent.Type.MouseMove:
                if self._drag_start_pos is None:
                    return False
                if not (event.buttons() & Qt.MouseButton.LeftButton):
                    return False
                moved = (
                    event.position().toPoint() - self._drag_start_pos
                ).manhattanLength()
                if moved < 8:
                    return False
                self._start_drag()
                return True
            if event.type() == QEvent.Type.MouseButtonRelease:
                self._drag_start_pos = None

        return super().eventFilter(obj, event)

    def _start_drag(self) -> None:
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(MIME_TYPE, b"card")
        drag.setMimeData(mime)

        snapshot: QPixmap = self.grab()
        transparent = QPixmap(snapshot.size())
        transparent.fill(Qt.GlobalColor.transparent)
        p = QPainter(transparent)
        p.drawPixmap(0, 0, snapshot)
        p.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_DestinationIn
        )
        p.fillRect(transparent.rect(), QColor(0, 0, 0, 140))
        p.end()
        pixmap = transparent
        pixmap = pixmap.scaled(
            int(pixmap.width() * 0.55),
            int(pixmap.height() * 0.55),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap.width() // 2, 20))

        drag.exec(Qt.DropAction.MoveAction)
        self._drag_start_pos = None