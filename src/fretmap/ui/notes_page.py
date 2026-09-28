"""Страница режима подбора нот — основное приложение."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ..music.instruments import INSTRUMENTS_BY_ID
from ..music.theory import SCALE_DISPLAY_NAMES, Scale, note_name, parse_note
from ..music.tunings import ALL_TUNINGS_BY_ID
from . import preset_manager, settings
from .add_dialog import AddInstrumentDialog
from .cards_container import CardsContainer
from .instrument_card import InstrumentCard
from .instrument_view import InstrumentView
from .presets_menu import PresetsButton
from .save_preset_dialog import SavePresetDialog
from .settings_dialog import SettingsDialog
from .theme import apply_theme


ROOT_NOTES = [
    "C", "C#", "Db", "D", "D#", "Eb", "E", "F",
    "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B",
]


class NotesPage(QWidget):
    """Страница с текущим функционалом fretmap."""

    back_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._cards: list[InstrumentCard] = []
        self._build_ui()
        self._update_workspace_hint()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # --- Верхняя панель ---
        top = QHBoxLayout()
        top.setSpacing(12)

        back_btn = QPushButton("← Назад")
        back_btn.setToolTip("Вернуться в главное меню")
        back_btn.clicked.connect(self.back_requested.emit)
        top.addWidget(back_btn)

        top.addSpacing(12)

        title = QLabel("Режим подбора нот")
        title.setObjectName("topTitle")
        top.addWidget(title)

        top.addSpacing(20)

        self.global_root_label = QLabel("Общая тональность:")
        self.global_root_label.setObjectName("fieldLabel")
        top.addWidget(self.global_root_label)

        self.global_root_combo = QComboBox()
        self.global_root_combo.addItems(ROOT_NOTES)
        self.global_root_combo.setCurrentText("C")
        self.global_root_combo.setMinimumWidth(80)
        self.global_root_combo.currentIndexChanged.connect(
            self._on_global_root_changed
        )
        top.addWidget(self.global_root_combo)

        top.addSpacing(12)

        self.global_scale_label = QLabel("Общий лад:")
        self.global_scale_label.setObjectName("fieldLabel")
        top.addWidget(self.global_scale_label)

        self.global_scale_combo = QComboBox()
        for key, display in SCALE_DISPLAY_NAMES.items():
            self.global_scale_combo.addItem(display, key)
        self.global_scale_combo.setCurrentText("Ионийский (мажор)")
        self.global_scale_combo.setMinimumWidth(180)
        self.global_scale_combo.currentIndexChanged.connect(
            self._on_global_scale_changed
        )
        top.addWidget(self.global_scale_combo)

        top.addStretch(1)

        self.presets_btn = PresetsButton()
        self.presets_btn.preset_selected.connect(self._apply_preset)
        self.presets_btn.save_requested.connect(self._save_current_as_preset)
        top.addWidget(self.presets_btn)

        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.clicked.connect(self._open_settings)
        top.addWidget(self.settings_btn)

        root.addLayout(top)

        # --- Рабочий холст ---
        self.scroll = QScrollArea()
        self.scroll.setObjectName("workspace")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.scroll.setSizeAdjustPolicy(
            QScrollArea.SizeAdjustPolicy.AdjustIgnored
        )

        self.cards_container = CardsContainer()
        self.cards_container.drop_requested.connect(self._on_drop_requested)

        self.workspace_hint = QLabel(
            "Здесь будут ваши инструменты.\n\n"
            "Нажмите «+ Добавить инструмент» внизу, "
            "чтобы создать первую карточку."
        )
        self.workspace_hint.setObjectName("workspaceHint")
        self.workspace_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cards_container.layout.addWidget(self.workspace_hint)
        self.cards_container.layout.addStretch(1)

        self.scroll.setWidget(self.cards_container)
        root.addWidget(self.scroll, stretch=1)

        # --- Нижняя панель ---
        bottom = QHBoxLayout()
        bottom.addStretch(1)

        self.add_btn = QPushButton("+ Добавить инструмент")
        self.add_btn.setObjectName("primary")
        self.add_btn.setMinimumHeight(36)
        self.add_btn.setMinimumWidth(220)
        self.add_btn.clicked.connect(self._on_add_clicked)
        bottom.addWidget(self.add_btn)

        bottom.addStretch(1)
        root.addLayout(bottom)

    # ---------- карточки ----------

    def _update_workspace_hint(self) -> None:
        self.workspace_hint.setVisible(len(self._cards) == 0)

    def _on_add_clicked(self) -> None:
        dialog = AddInstrumentDialog(self)
        if dialog.exec() != AddInstrumentDialog.DialogCode.Accepted:
            return
        view = dialog.get_view()
        if view is None:
            return
        self._add_card(view)

    def _add_card(self, view: InstrumentView) -> None:
        card = InstrumentCard(view)
        card.remove_requested.connect(self._on_card_remove)
        self._cards.append(card)
        self._relayout_cards()
        self._update_workspace_hint()

    def _on_card_remove(self, card: InstrumentCard) -> None:
        if card in self._cards:
            self._cards.remove(card)
        card.setParent(None)
        card.deleteLater()
        self._relayout_cards()
        self._update_workspace_hint()

    def _clear_all_cards(self) -> None:
        for card in list(self._cards):
            self._on_card_remove(card)

    def _relayout_cards(self) -> None:
        layout = self.cards_container.layout

        for c in self._cards:
            layout.removeWidget(c)

        layout.removeWidget(self.workspace_hint)

        for i in reversed(range(layout.count())):
            item = layout.itemAt(i)
            if item.spacerItem() is not None:
                layout.takeAt(i)
                break

        for i, c in enumerate(self._cards):
            layout.insertWidget(i, c)

        layout.addWidget(self.workspace_hint)
        layout.addStretch(1)

    # ---------- drop ----------

    def _on_drop_requested(self, source, target_index: int) -> None:
        if not isinstance(source, InstrumentCard):
            return
        if source not in self._cards:
            return

        current = self._cards.index(source)
        target = max(0, min(target_index, len(self._cards)))
        if target == current:
            return
        if target > current:
            target -= 1
        target = max(0, min(target, len(self._cards) - 1))
        if target == current:
            return

        self._cards.pop(current)
        self._cards.insert(target, source)
        self._relayout_cards()

    # ---------- общая тональность и лад ----------

    def _on_global_root_changed(self) -> None:
        root_name = self.global_root_combo.currentText()
        for card in self._cards:
            card.set_root_note(root_name)

    def _on_global_scale_changed(self) -> None:
        scale_name = self.global_scale_combo.currentData()
        for card in self._cards:
            card.set_scale_name(scale_name)

    # ---------- пресеты ----------

    def _apply_preset(self, preset: dict) -> None:
        cards = preset.get("cards", [])
        if not cards:
            return

        self._clear_all_cards()

        for item in cards:
            inst = INSTRUMENTS_BY_ID.get(item["instrument_id"])
            if inst is None:
                continue
            tuning = ALL_TUNINGS_BY_ID.get(item["tuning_id"])
            if tuning is None:
                continue

            root_midi = parse_note(f"{item['root_name']}4")
            prefer_flats = "b" in item["root_name"]
            scale = Scale(root_midi, item["scale_name"], prefer_flats=prefer_flats)

            view = InstrumentView(
                instrument=inst,
                tuning=tuning,
                scale=scale,
                fret_count=item.get("fret_count"),
            )
            self._add_card(view)

    def _save_current_as_preset(self) -> None:
        if not self._cards:
            QMessageBox.information(
                self, "Пусто", "Нет карточек для сохранения в пресет."
            )
            return

        dialog = SavePresetDialog("Мой пресет", self)
        if dialog.exec() != SavePresetDialog.DialogCode.Accepted:
            return

        name = dialog.preset_name()
        if not name:
            return

        cards: list[dict] = []
        for card in self._cards:
            v = card.view
            cards.append({
                "instrument_id": v.instrument.id,
                "tuning_id": v.tuning.id,
                "root_name": note_name(v.scale.root_midi, v.scale.prefer_flats),
                "scale_name": v.scale.scale_name,
                "fret_count": v.effective_fret_count(),
            })

        path = preset_manager.save_preset(name, cards)
        if path is None:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить пресет.")
            return

        self.presets_btn._build_menu()
        QMessageBox.information(self, "Готово", f"Пресет «{name}» сохранён.")

    # ---------- настройки ----------

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self)
        dialog.applied.connect(self._apply_appearance)
        dialog.exec()

    def _apply_appearance(self) -> None:
        app = QApplication.instance()
        if app is None:
            return
        apply_theme(
            app,
            theme_name=settings.get_theme(),
            accent_override=settings.get_accent() or None,
            font_size=settings.get_font_size(),
        )
        for w in app.allWidgets():
            w.update()