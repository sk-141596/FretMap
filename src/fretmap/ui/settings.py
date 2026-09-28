"""Обёртка над QSettings для хранения пользовательских настроек."""

from __future__ import annotations

from PySide6.QtCore import QSettings


_settings = QSettings("fretmap", "fretmap")

# Дефолтный акцент — тёмный бирюзовый
DEFAULT_ACCENT = "#3a8a8a"

# Дефолтные цвета кружков нот на грифе
DEFAULT_NOTE_COLOR = "#005c54"
DEFAULT_TONIC_COLOR = "#038f65"


def _flush() -> None:
    _settings.sync()


def get_theme() -> str:
    value = _settings.value("appearance/theme", "nord", type=str)
    return value or "nord"


def set_theme(name: str) -> None:
    _settings.setValue("appearance/theme", name)
    _flush()


def get_accent() -> str:
    value = _settings.value("appearance/accent", DEFAULT_ACCENT, type=str)
    return value if value else DEFAULT_ACCENT


def set_accent(color: str) -> None:
    _settings.setValue("appearance/accent", color)
    _flush()


def get_note_color() -> str:
    value = _settings.value("appearance/note_color", DEFAULT_NOTE_COLOR, type=str)
    return value if value else DEFAULT_NOTE_COLOR


def set_note_color(color: str) -> None:
    _settings.setValue("appearance/note_color", color)
    _flush()


def get_tonic_color() -> str:
    value = _settings.value("appearance/tonic_color", DEFAULT_TONIC_COLOR, type=str)
    return value if value else DEFAULT_TONIC_COLOR


def set_tonic_color(color: str) -> None:
    _settings.setValue("appearance/tonic_color", color)
    _flush()


def get_font_size() -> int:
    value = _settings.value("appearance/font_size", 10, type=int)
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = 10
    return max(8, min(14, value))


def set_font_size(size: int) -> None:
    _settings.setValue("appearance/font_size", int(size))
    _flush()


def get_note_scale() -> float:
    value = _settings.value("appearance/note_scale", 1.0, type=float)
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 1.0
    return max(0.7, min(1.4, value))


def set_note_scale(value: float) -> None:
    _settings.setValue("appearance/note_scale", float(value))
    _flush()