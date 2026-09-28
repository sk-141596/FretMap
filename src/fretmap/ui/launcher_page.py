"""Стартовая страница с меню режимов."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class LauncherPage(QWidget):
    """Стартовое меню: выбор режима.

    Сигнал notes_requested эмитится при нажатии на «Режим подбора нот».
    """

    notes_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(20)
        root.addStretch(1)

        # Заголовок
        title = QLabel("fretmap")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 32pt; font-weight: bold; padding: 10px;"
        )
        root.addWidget(title)

        subtitle = QLabel("Интерактивная карта нот на грифе")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 12pt; padding-bottom: 20px;")
        root.addWidget(subtitle)

        # Кнопки
        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(20)
        buttons_row.addStretch(1)

        # Кнопка 1 — активная
        notes_btn = QPushButton("Режим подбора нот")
        notes_btn.setObjectName("launcherButton")
        notes_btn.setMinimumSize(280, 120)
        notes_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        notes_btn.setToolTip("Настройка инструментов, строёв и гамм")
        notes_btn.clicked.connect(self.notes_requested.emit)
        buttons_row.addWidget(notes_btn)

        # Кнопка 2 — заглушка
        exercises_btn = QPushButton("Музыкальные упражнения")
        exercises_btn.setObjectName("launcherButtonDisabled")
        exercises_btn.setMinimumSize(280, 120)
        exercises_btn.setEnabled(False)
        exercises_btn.setToolTip("Скоро: упражнения для тренировки")
        buttons_row.addWidget(exercises_btn)

        buttons_row.addStretch(1)
        root.addLayout(buttons_row)

        root.addStretch(2)