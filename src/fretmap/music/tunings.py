"""Строи для струнных инструментов."""

from __future__ import annotations

from dataclasses import dataclass

from .theory import parse_note


@dataclass(frozen=True)
class Tuning:
    id: str
    display_name: str
    strings_midi: tuple[int, ...]

    @property
    def string_count(self) -> int:
        return len(self.strings_midi)

    def note_names(self, prefer_flats: bool = False) -> list[str]:
        from .theory import note_name
        return [note_name(m, prefer_flats) for m in self.strings_midi]


GUITAR_TUNINGS: list[Tuning] = [
    Tuning("standard_e", "Standard E (EADGBE)",
           tuple(parse_note(n) for n in ["E2", "A2", "D3", "G3", "B3", "E4"])),
    Tuning("standard_eb", "Standard Eb (Eb Ab Db Gb Bb Eb)",
           tuple(parse_note(n) for n in ["Eb2", "Ab2", "Db3", "Gb3", "Bb3", "Eb4"])),
    Tuning("standard_d", "Standard D (DGCFAD)",
           tuple(parse_note(n) for n in ["D2", "G2", "C3", "F3", "A3", "D4"])),
    Tuning("drop_d", "Drop D (DADGBE)",
           tuple(parse_note(n) for n in ["D2", "A2", "D3", "G3", "B3", "E4"])),
    Tuning("drop_c", "Drop C (CGCFAD)",
           tuple(parse_note(n) for n in ["C2", "G2", "C3", "F3", "A3", "D4"])),
    Tuning("dadgad", "DADGAD",
           tuple(parse_note(n) for n in ["D2", "A2", "D3", "G3", "A3", "D4"])),
    Tuning("open_g", "Open G (DGDGBD)",
           tuple(parse_note(n) for n in ["D2", "G2", "D3", "G3", "B3", "D4"])),
    Tuning("open_d", "Open D (DADF#AD)",
           tuple(parse_note(n) for n in ["D2", "A2", "D3", "F#3", "A3", "D4"])),
]


GUITAR_7_TUNINGS: list[Tuning] = [
    Tuning("standard_b", "Standard B (BEADGBE)",
           tuple(parse_note(n) for n in ["B1", "E2", "A2", "D3", "G3", "B3", "E4"])),
    Tuning("drop_a", "Drop A (AEADGBE)",
           tuple(parse_note(n) for n in ["A1", "E2", "A2", "D3", "G3", "B3", "E4"])),
]


BASS_TUNINGS: list[Tuning] = [
    Tuning("standard_bass", "Standard (EADG)",
           tuple(parse_note(n) for n in ["E1", "A1", "D2", "G2"])),
    Tuning("drop_d_bass", "Drop D (DADG)",
           tuple(parse_note(n) for n in ["D1", "A1", "D2", "G2"])),
    Tuning("bass_d_standard", "D Standard (DGCF)",
           tuple(parse_note(n) for n in ["D1", "G1", "C2", "F2"])),
    Tuning("bass_eb", "Eb Standard (Eb Ab Db Gb)",
           tuple(parse_note(n) for n in ["Eb1", "Ab1", "Db2", "Gb2"])),
]


BASS_5_TUNINGS: list[Tuning] = [
    Tuning("standard_bass_5", "Standard 5 (BEADG)",
           tuple(parse_note(n) for n in ["B0", "E1", "A1", "D2", "G2"])),
    Tuning("drop_a_bass", "Drop A (AEADG)",
           tuple(parse_note(n) for n in ["A0", "E1", "A1", "D2", "G2"])),
]


NO_TUNING = Tuning(
    id="_none",
    display_name="—",
    strings_midi=(),
)


ALL_TUNINGS_BY_ID: dict[str, Tuning] = {
    t.id: t
    for t in (
        GUITAR_TUNINGS
        + GUITAR_7_TUNINGS
        + BASS_TUNINGS
        + BASS_5_TUNINGS
        + [NO_TUNING]
    )
}