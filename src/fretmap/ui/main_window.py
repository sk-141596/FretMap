"""Главное окно fretmap: контейнер страниц."""

from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QStackedWidget

from .launcher_page import LauncherPage
from .notes_page import NotesPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("fretmap")
        self.resize(1500, 900)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._launcher = LauncherPage()
        self._launcher.notes_requested.connect(self._show_notes)

        self._notes = NotesPage()
        self._notes.back_requested.connect(self._show_launcher)

        self._stack.addWidget(self._launcher)
        self._stack.addWidget(self._notes)

        self._stack.setCurrentWidget(self._launcher)

    def _show_notes(self) -> None:
        self._stack.setCurrentWidget(self._notes)

    def _show_launcher(self) -> None:
        self._stack.setCurrentWidget(self._launcher)