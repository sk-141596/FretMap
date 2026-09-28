"""Встроенные пресеты: список карточек с инструментом, строем, тональностью, ладом."""

from __future__ import annotations


# Каждая запись в пресете = одна карточка.
# Поля: instrument_id, tuning_id, root_name, scale_name, fret_count.
BUILTIN_PRESETS: list[dict] = [
    {
        "name": "Гитара + Бас: Стандарт (E)",
        "cards": [
            {
                "instrument_id": "guitar_6",
                "tuning_id": "standard_e",
                "root_name": "C",
                "scale_name": "ionian",
                "fret_count": 22,
            },
            {
                "instrument_id": "bass_4",
                "tuning_id": "standard_bass",
                "root_name": "C",
                "scale_name": "ionian",
                "fret_count": 20,
            },
        ],
    },
    {
        "name": "Гитара + Бас: Drop D",
        "cards": [
            {
                "instrument_id": "guitar_6",
                "tuning_id": "drop_d",
                "root_name": "D",
                "scale_name": "mixolydian",
                "fret_count": 22,
            },
            {
                "instrument_id": "bass_4",
                "tuning_id": "drop_d_bass",
                "root_name": "D",
                "scale_name": "mixolydian",
                "fret_count": 20,
            },
        ],
    },
    {
        "name": "Гитара + Бас: D Standard",
        "cards": [
            {
                "instrument_id": "guitar_6",
                "tuning_id": "standard_d",
                "root_name": "D",
                "scale_name": "aeolian",
                "fret_count": 22,
            },
            {
                "instrument_id": "bass_4",
                "tuning_id": "bass_d_standard",
                "root_name": "D",
                "scale_name": "aeolian",
                "fret_count": 20,
            },
        ],
    },
    {
        "name": "Гитара: Open G + Бас: Стандарт",
        "cards": [
            {
                "instrument_id": "guitar_6",
                "tuning_id": "open_g",
                "root_name": "G",
                "scale_name": "major_pentatonic",
                "fret_count": 22,
            },
            {
                "instrument_id": "bass_4",
                "tuning_id": "standard_bass",
                "root_name": "G",
                "scale_name": "major_pentatonic",
                "fret_count": 20,
            },
        ],
    },
    {
        "name": "Гитара: DADGAD + Бас: Drop D",
        "cards": [
            {
                "instrument_id": "guitar_6",
                "tuning_id": "dadgad",
                "root_name": "D",
                "scale_name": "mixolydian",
                "fret_count": 22,
            },
            {
                "instrument_id": "bass_4",
                "tuning_id": "drop_d_bass",
                "root_name": "D",
                "scale_name": "mixolydian",
                "fret_count": 20,
            },
        ],
    },
]