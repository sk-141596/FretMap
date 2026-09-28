"""Модель «инструмент на экране»."""

from __future__ import annotations

from dataclasses import dataclass

from ..music.instruments import Instrument
from ..music.theory import Scale
from ..music.tunings import Tuning


@dataclass
class InstrumentView:
    """Один инструмент, отображаемый на экране."""

    instrument: Instrument
    tuning: Tuning
    scale: Scale
    show_degrees: bool = False
    show_full_range: bool = False
    fret_count: int | None = None

    def effective_fret_count(self) -> int:
        if self.fret_count is not None:
            return self.fret_count
        return self.instrument.fret_count