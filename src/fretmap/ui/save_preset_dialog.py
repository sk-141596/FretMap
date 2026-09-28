"""Диалог сохранения пресета."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
)


class SavePresetDialog(QDialog):
    """Диалог ввода имени пресета."""

    def __init__(self, default_name: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Сохранить пресет")
        self.setMinimumWidth(360)

        root = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setText(default_name)
        self.name_edit.setPlaceholderText("Например: «Гитара + Бас: Drop D»")
        form.addRow("Название:", self.name_edit)

        root.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_ok)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _on_ok(self) -> None:
        if self.name_edit.text().strip():
            self.accept()

    def preset_name(self) -> str:
        return self.name_edit.text().strip()