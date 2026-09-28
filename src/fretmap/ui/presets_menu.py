"""Выпадающее меню пресетов: встроенные + кастомные + сохранение."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMenu, QToolButton, QWidget

from . import preset_manager
from .presets import BUILTIN_PRESETS


class PresetsButton(QToolButton):
    """Кнопка с выпадающим меню пресетов.

    Сигналы:
    - preset_selected: выбран встроенный или кастомный пресет (dict с ключом cards)
    - save_requested: пользователь хочет сохранить текущий набор как пресет
    """

    preset_selected = Signal(dict)
    save_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setText("Пресеты ▾")
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._build_menu()

    def _build_menu(self) -> None:
        menu = QMenu(self)

        # --- Встроенные ---
        builtin_menu = menu.addMenu("Встроенные")
        for preset in BUILTIN_PRESETS:
            action = builtin_menu.addAction(preset["name"])
            action.triggered.connect(
                lambda checked=False, p=preset: self.preset_selected.emit(p)
            )

        # --- Кастомные ---
        custom_menu = menu.addMenu("Мои пресеты")
        custom = preset_manager.list_custom_presets()
        if custom:
            for name, path in custom:
                action = custom_menu.addAction(name)
                action.triggered.connect(
                    lambda checked=False, p=path: self._load_custom(p)
                )
        else:
            empty = custom_menu.addAction("(пусто)")
            empty.setEnabled(False)

        menu.addSeparator()

        save_action = menu.addAction("Сохранить текущий как пресет…")
        save_action.triggered.connect(self.save_requested.emit)

        refresh_action = menu.addAction("Обновить список")
        refresh_action.triggered.connect(self._refresh_menu)

        self.setMenu(menu)

    def _load_custom(self, path) -> None:
        data = preset_manager.load_preset(path)
        if data is not None:
            self.preset_selected.emit(data)

    def _refresh_menu(self) -> None:
        self._build_menu()