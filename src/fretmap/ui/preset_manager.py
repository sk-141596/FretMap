"""Управление кастомными пресетами пользователя."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths


def _presets_dir() -> Path:
    """Папка для хранения кастомных пресетов пользователя."""
    base = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    )
    if not base:
        base = str(Path.home() / ".fretmap")
    d = Path(base) / "presets"
    d.mkdir(parents=True, exist_ok=True)
    return d


def list_custom_presets() -> list[tuple[str, Path]]:
    """Вернуть список (имя, путь) для всех кастомных пресетов."""
    result: list[tuple[str, Path]] = []
    for p in sorted(_presets_dir().glob("*.json")):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("name", p.stem)
            result.append((name, p))
        except (OSError, json.JSONDecodeError):
            continue
    return result


def load_preset(path: Path) -> dict | None:
    """Загрузить пресет из файла. Вернуть словарь или None."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def save_preset(name: str, cards: list[dict]) -> Path | None:
    """Сохранить пресет в папку пользователя. Вернуть путь или None."""
    safe = "".join(
        c if c.isalnum() or c in " _-." else "_" for c in name
    ).strip() or "preset"
    path = _presets_dir() / f"{safe}.json"

    data = {"name": name, "cards": cards}
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path
    except OSError:
        return None


def delete_preset(path: Path) -> bool:
    """Удалить пресет."""
    try:
        path.unlink()
        return True
    except OSError:
        return False