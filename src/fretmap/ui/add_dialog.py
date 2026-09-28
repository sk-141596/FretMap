"""Диалог добавления инструмента."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)

from ..music.instruments import ALL_INSTRUMENTS, Instrument
from ..music.theory import SCALE_DISPLAY_NAMES, Scale, parse_note
from ..music.tunings import NO_TUNING
from .instrument_view import InstrumentView


ROOT_NOTES = [
    "C", "C#", "Db", "D", "D#", "Eb", "E", "F",
    "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B",
]


class AddInstrumentDialog(QDialog):
    """Диалог добавления инструмента с выбором всех параметров."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Добавить инструмент")
        self.setMinimumWidth(420)

        self._view: InstrumentView | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(8)

        self.instrument_combo = QComboBox()
        for inst in ALL_INSTRUMENTS:
            self.instrument_combo.addItem(inst.display_name, inst.id)
        form.addRow("Инструмент:", self.instrument_combo)

        self.tuning_label = QLabel("Строй:")
        self.tuning_combo = QComboBox()
        form.addRow(self.tuning_label, self.tuning_combo)

        self.frets_label = QLabel("Ладов:")
        self.frets_combo = QComboBox()
        form.addRow(self.frets_label, self.frets_combo)

        self.root_combo = QComboBox()
        self.root_combo.addItems(ROOT_NOTES)
        self.root_combo.setCurrentText("C")
        form.addRow("Тоника:", self.root_combo)

        self.scale_combo = QComboBox()
        for key, display in SCALE_DISPLAY_NAMES.items():
            self.scale_combo.addItem(display, key)
        self.scale_combo.setCurrentText("Ионийский (мажор)")
        form.addRow("Лад:", self.scale_combo)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Ноты", "notes")
        self.mode_combo.addItem("Ступени", "degrees")
        form.addRow("Подписи:", self.mode_combo)

        root.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self._reload_for_instrument()
        self.instrument_combo.currentIndexChanged.connect(
            lambda: self._reload_for_instrument()
        )

    def _current_instrument(self) -> Instrument | None:
        inst_id = self.instrument_combo.currentData()
        if inst_id is None:
            return None
        for inst in ALL_INSTRUMENTS:
            if inst.id == inst_id:
                return inst
        return None

    def _reload_for_instrument(self) -> None:
        inst = self._current_instrument()
        if inst is None:
            return

        # Строи
        self.tuning_combo.blockSignals(True)
        self.tuning_combo.clear()
        if inst.tunings:
            for t in inst.tunings:
                self.tuning_combo.addItem(t.display_name, t.id)
            self.tuning_label.setVisible(True)
            self.tuning_combo.setVisible(True)
        else:
            self.tuning_combo.addItem(NO_TUNING.display_name, NO_TUNING.id)
            self.tuning_label.setVisible(False)
            self.tuning_combo.setVisible(False)
        self.tuning_combo.blockSignals(False)

        # Лады
        self.frets_combo.blockSignals(True)
        self.frets_combo.clear()
        if inst.is_stringed:
            lo, hi = inst.fret_range
            std = inst.fret_count
            self.frets_combo.addItem(f"Стандарт ({std} ладов)", std)
            for n in range(lo, hi + 1):
                if n != std:
                    self.frets_combo.addItem(f"{n} ладов", n)
            self.frets_label.setVisible(True)
            self.frets_combo.setVisible(True)
        else:
            self.frets_label.setVisible(False)
            self.frets_combo.setVisible(False)
        self.frets_combo.blockSignals(False)

    def _on_accept(self) -> None:
        inst = self._current_instrument()
        if inst is None:
            QMessageBox.warning(self, "Ошибка", "Инструмент не выбран.")
            return

        if inst.tunings:
            tuning_id = self.tuning_combo.currentData()
            tuning = None
            for t in inst.tunings:
                if t.id == tuning_id:
                    tuning = t
                    break
            if tuning is None:
                QMessageBox.warning(
                    self, "Ошибка", "Для выбранного инструмента строй не задан."
                )
                return
        else:
            tuning = NO_TUNING

        root_name = self.root_combo.currentText()
        root_midi = parse_note(f"{root_name}4")
        prefer_flats = "b" in root_name
        scale = Scale(root_midi, self.scale_combo.currentData(), prefer_flats=prefer_flats)

        show_degrees = self.mode_combo.currentData() == "degrees"

        fret_count: int | None = None
        if inst.is_stringed:
            sel = self.frets_combo.currentData()
            if sel is not None and sel != inst.fret_count:
                fret_count = sel

        self._view = InstrumentView(
            instrument=inst,
            tuning=tuning,
            scale=scale,
            show_degrees=show_degrees,
            fret_count=fret_count,
        )
        self.accept()

    def get_view(self) -> InstrumentView | None:
        return self._view