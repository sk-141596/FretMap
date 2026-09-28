"""Доступ к ресурсам приложения (иконки и т.п.)."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QIcon


def _resource_path(relative: str) -> Path:
    """Найти ресурс и в бандле PyInstaller, и при запуске из исходников."""
    if getattr(sys, "_MEIPASS", None):
        base = Path(sys._MEIPASS)
        return base / "fretmap" / "ui" / relative
    return Path(__file__).parent / relative


def app_icon() -> QIcon:
    """Иконка приложения.

    Если .ico отсутствует — вернёт пустую QIcon, приложение
    запустится без иконки.
    """
    ico = _resource_path("icon.ico")
    if ico.is_file():
        return QIcon(str(ico))
    return QIcon()