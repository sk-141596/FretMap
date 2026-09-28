"""Описания инструментов: гитара, бас, фортепиано."""

from __future__ import annotations

from dataclasses import dataclass

from .tunings import (
    BASS_5_TUNINGS,
    BASS_TUNINGS,
    GUITAR_7_TUNINGS,
    GUITAR_TUNINGS,
    Tuning,
)


FRET_COUNT_TO_MODELS: dict[int, list[str]] = {
    19: ["Precision Bass (винтаж)"],
    20: ["Precision Bass", "Jazz Bass"],
    21: ["Stratocaster (классика)", "Telecaster (классика)", "Jazzmaster"],
    22: ["Les Paul", "SG", "Yamaha SG", "Stratocaster (совр.)"],
    24: ["Ibanez RG", "Jackson Soloist", "ESP LTD", "PRS Custom 24"],
}


def models_for_frets(fret_count: int) -> str:
    """Вернуть строку с моделями для заданного числа ладов."""
    models = FRET_COUNT_TO_MODELS.get(fret_count, [])
    return ", ".join(models) if models else ""


@dataclass(frozen=True)
class Instrument:
    """Инструмент: id, отображаемое имя, строи, лады (для струнных)."""

    id: str
    display_name: str
    tunings: tuple[Tuning, ...] = ()
    fret_count: int = 0
    midi_range: tuple[int, int] | None = None
    wood_style: str = "rosewood"
    model_name: str = ""
    fret_range: tuple[int, int] = (0, 0)

    @property
    def is_stringed(self) -> bool:
        return bool(self.tunings)

    @property
    def is_keyboard(self) -> bool:
        return self.midi_range is not None

    def default_tuning(self) -> Tuning | None:
        return self.tunings[0] if self.tunings else None


GUITAR_6 = Instrument(
    id="guitar_6",
    display_name="Гитара (6 струн)",
    tunings=tuple(GUITAR_TUNINGS),
    fret_count=22,
    wood_style="rosewood",
    model_name="Les Paul / SG",
    fret_range=(21, 24),
)

GUITAR_7 = Instrument(
    id="guitar_7",
    display_name="Гитара (7 струн)",
    tunings=tuple(GUITAR_7_TUNINGS),
    fret_count=24,
    wood_style="ebony",
    model_name="Ibanez RG / Jackson Soloist",
    fret_range=(22, 24),
)

BASS_4 = Instrument(
    id="bass_4",
    display_name="Бас (4 струны)",
    tunings=tuple(BASS_TUNINGS),
    fret_count=20,
    wood_style="maple",
    model_name="Precision Bass / Jazz Bass",
    fret_range=(19, 22),
)

BASS_5 = Instrument(
    id="bass_5",
    display_name="Бас (5 струн)",
    tunings=tuple(BASS_5_TUNINGS),
    fret_count=22,
    wood_style="walnut",
    model_name="Ibanez SR / Gio",
    fret_range=(20, 24),
)

PIANO_88 = Instrument(
    id="piano_88",
    display_name="Фортепиано (88 клавиш)",
    midi_range=(21, 108),
)

KEYBOARD_61 = Instrument(
    id="keyboard_61",
    display_name="Клавиатура (61 клавиша)",
    midi_range=(36, 96),
)


ALL_INSTRUMENTS: list[Instrument] = [
    GUITAR_6,
    GUITAR_7,
    BASS_4,
    BASS_5,
    PIANO_88,
    KEYBOARD_61,
]

INSTRUMENTS_BY_ID: dict[str, Instrument] = {i.id: i for i in ALL_INSTRUMENTS}