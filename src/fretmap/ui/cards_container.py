"""Контейнер карточек. Принимает drop от перетаскиваемых карточек."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget


MIME_TYPE = "application/x-fretmap-card"


class CardsContainer(QWidget):
    """Вертикальный контейнер карточек с поддержкой drag & drop.

    Принимает drop, вычисляет индекс по позиции мыши и сообщает
    главному окну, куда вставить перетаскиваемую карточку.
    """

    drop_requested = Signal(object, int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(12)

    # ---------- drag & drop ----------

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasFormat(MIME_TYPE):
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasFormat(MIME_TYPE):
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        if not event.mimeData().hasFormat(MIME_TYPE):
            return

        source = event.source()
        if source is None:
            return

        pos = event.position().toPoint()
        target_index = self._index_at(pos)

        self.drop_requested.emit(source, target_index)
        event.acceptProposedAction()

    def _index_at(self, pos) -> int:
        """Вернуть индекс карточки, перед которой нужно вставить."""
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            w = item.widget()
            if w is None:
                continue
            top = w.y()
            bottom = top + w.height()
            if pos.y() < top:
                return i
            if top <= pos.y() <= bottom:
                if pos.y() < top + w.height() / 2:
                    return i
                return i + 1
        return self.layout.count()