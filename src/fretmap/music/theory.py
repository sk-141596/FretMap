"""Музыкальная теория: ноты, интервалы, гаммы, аккорды.

Всё в MIDI-нотах: C-1 = 0, C4 = 60, A4 = 69. Каждая октава — 12 полутонов.
Названия нот отображаются отдельно, потому что одну и ту же высоту можно
назвать по-разному (C# / Db) в зависимости от контекста.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------- Ноты ----------------

# Полутоновые смещения для базовых нот (C = 0, C# = 1, ...)
NOTE_NAMES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTE_NAMES_FLAT = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

# Буквы без полутонов (для построения гамм) и их «естественные» позиции
NATURAL_NOTES = {
    "C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11,
}


def midi_to_pitch_class(midi: int) -> int:
    """Полутон внутри октавы (0-11)."""
    return midi % 12


def note_name(midi: int, prefer_flats: bool = False) -> str:
    """Название ноты без октавы."""
    table = NOTE_NAMES_FLAT if prefer_flats else NOTE_NAMES_SHARP
    return table[midi_to_pitch_class(midi)]


def note_name_with_octave(midi: int, prefer_flats: bool = False) -> str:
    """Полное имя ноты с октавой: C4, A#3, Eb5."""
    name = note_name(midi, prefer_flats)
    # Октава по научной нотации: C4 = 60, значит октава = midi // 12 - 1
    octave = midi // 12 - 1
    return f"{name}{octave}"


def parse_note(s: str) -> int:
    """Разобрать строку ноты в MIDI-число.

    Поддерживает: "C", "C#", "Db", "C4", "A#3", "Eb5".
    Регистр не важен. Если октава не указана — используется 4.
    """
    s = s.strip()
    if not s:
        raise ValueError("Пустая строка ноты")

    # Отделяем букву
    letter = s[0].upper()
    if letter not in "ABCDEFG":
        raise ValueError(f"Неизвестная нота: {s}")

    pos = 1
    semitone = NATURAL_NOTES[letter]

    # Знаки альтерации: # или b (может быть несколько, но у нас — один)
    while pos < len(s) and s[pos] in "#b":
        if s[pos] == "#":
            semitone += 1
        else:
            semitone -= 1
        pos += 1

    # Октава
    octave = 4
    if pos < len(s):
        try:
            octave = int(s[pos:])
        except ValueError as e:
            raise ValueError(f"Не удалось разобрать октаву в {s!r}") from e

    midi = (octave + 1) * 12 + semitone
    if not 0 <= midi <= 127:
        raise ValueError(f"Нота {s!r} вышла за диапазон MIDI (0-127)")
    return midi


# ---------------- Интервалы ----------------

class Interval(Enum):
    """Простые интервалы в полутонах."""
    UNISON = 0
    MINOR_SECOND = 1
    MAJOR_SECOND = 2
    MINOR_THIRD = 3
    MAJOR_THIRD = 4
    PERFECT_FOURTH = 5
    TRITONE = 6
    PERFECT_FIFTH = 7
    MINOR_SIXTH = 8
    MAJOR_SIXTH = 9
    MINOR_SEVENTH = 10
    MAJOR_SEVENTH = 11
    OCTAVE = 12


# ---------------- Лады и гаммы ----------------

# Каждая гамма — список полутоновых смещений от тоники.
# Например, мажор (ионийский): 0, 2, 4, 5, 7, 9, 11 = целый-целый-полутон-...
SCALES: dict[str, list[int]] = {
    # Мажорные лады (греческие)
    "ionian":     [0, 2, 4, 5, 7, 9, 11],   # мажор
    "dorian":     [0, 2, 3, 5, 7, 9, 10],
    "phrygian":   [0, 1, 3, 5, 7, 8, 10],
    "lydian":     [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "aeolian":    [0, 2, 3, 5, 7, 8, 10],   # натуральный минор
    "locrian":    [0, 1, 3, 5, 6, 8, 10],

    # Пентатоники
    "major_pentatonic": [0, 2, 4, 7, 9],
    "minor_pentatonic": [0, 3, 5, 7, 10],

    # Блюзовые
    "blues_major": [0, 2, 3, 4, 7, 9],
    "blues_minor": [0, 3, 5, 6, 7, 10],

    # Гармонический и мелодический минор
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor":  [0, 2, 3, 5, 7, 9, 11],
}


# Русские/английские названия для отображения в UI
SCALE_DISPLAY_NAMES: dict[str, str] = {
    "ionian":           "Ионийский (мажор)",
    "dorian":           "Дорийский",
    "phrygian":         "Фригийский",
    "lydian":           "Лидийский",
    "mixolydian":       "Миксолидийский",
    "aeolian":          "Эолийский (минор)",
    "locrian":          "Локрийский",
    "major_pentatonic": "Мажорная пентатоника",
    "minor_pentatonic": "Минорная пентатоника",
    "blues_major":      "Мажорный блюз",
    "blues_minor":      "Минорный блюз",
    "harmonic_minor":   "Гармонический минор",
    "melodic_minor":    "Мелодический минор",
}


@dataclass
class Scale:
    """Конкретная гамма: тоника + лад."""

    root_midi: int          # MIDI-нота тоники (например, C4 = 60)
    scale_name: str         # ключ в SCALES
    prefer_flats: bool = False

    @property
    def intervals(self) -> list[int]:
        """Полутоновые смещения от тоники."""
        return SCALES[self.scale_name]

    @property
    def notes(self) -> list[int]:
        """MIDI-ноты гаммы в пределах одной октавы от тоники."""
        return [self.root_midi + i for i in self.intervals]

    @property
    def pitch_classes(self) -> set[int]:
        """Множество полутонов (0-11), входящих в гамму."""
        return {n % 12 for n in self.notes}

    def contains(self, midi: int) -> bool:
        """Входит ли нота в гамму (в любой октаве)."""
        return (midi % 12) in self.pitch_classes

    def degree(self, midi: int) -> int | None:
        """Ступень ноты в гамме (1-based). None, если нота не входит.

        Для пентатоник и блюзовых гамм ступень — это индекс + 1 в списке
        интервалов, что не всегда совпадает с классической нумерацией,
        но для UI этого достаточно.
        """
        pc = midi % 12
        root_pc = self.root_midi % 12
        offset = (pc - root_pc) % 12
        if offset not in self.intervals:
            return None
        return self.intervals.index(offset) + 1

    def note_names(self) -> list[str]:
        """Названия нот гаммы по порядку."""
        return [note_name(n, self.prefer_flats) for n in self.notes]

    def display_name(self) -> str:
        """Человекочитаемое название: 'C Ионийский (мажор)'."""
        root = note_name(self.root_midi, self.prefer_flats)
        scale = SCALE_DISPLAY_NAMES.get(self.scale_name, self.scale_name)
        return f"{root} {scale}"


# ---------------- Аккорды в тональности ----------------

# Трезвучия, построенные на ступенях мажорной гаммы:
# I - мажор, ii - минор, iii - минор, IV - мажор, V - мажор, vi - минор, vii - уменьшенный
MAJOR_DIATONIC_QUALITIES = ["", "m", "m", "", "", "m", "dim"]
MINOR_DIATONIC_QUALITIES = ["m", "dim", "", "m", "m", "", ""]


def diatonic_chords(scale: Scale) -> list[tuple[str, str]]:
    """Аккорды, построенные на ступенях гаммы.

    Возвращает список пар (название, качество) в порядке ступеней.
    Работает для ионийского (мажор) и эолийского (минор).
    Для остальных ладов возвращает мажорную логику — упрощение для MVP.
    """
    if scale.scale_name == "aeolian":
        qualities = MINOR_DIATONIC_QUALITIES
    else:
        qualities = MAJOR_DIATONIC_QUALITIES

    result: list[tuple[str, str]] = []
    for i, interval in enumerate(scale.intervals[:7]):
        if i >= len(qualities):
            break
        midi = scale.root_midi + interval
        name = note_name(midi, scale.prefer_flats)
        result.append((name, qualities[i]))
    return result