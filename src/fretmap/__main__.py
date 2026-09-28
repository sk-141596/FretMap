from __future__ import annotations

import sys

from PySide6.QtCore import QtMsgType, qInstallMessageHandler


def _qt_message_handler(mode: QtMsgType, context, message: str) -> None:
    if "QFont::setPointSize" in message:
        return
    sys.stderr.write(message + "\n")


qInstallMessageHandler(_qt_message_handler)

from PySide6.QtWidgets import QApplication  # noqa: E402

try:
    from .ui.main_window import MainWindow
    from .ui.resources import app_icon
    from .ui import settings
    from .ui.theme import apply_theme
except ImportError:
    from fretmap.ui.main_window import MainWindow
    from fretmap.ui.resources import app_icon
    from fretmap.ui import settings
    from fretmap.ui.theme import apply_theme


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("fretmap")
    app.setOrganizationName("fretmap")
    app.setWindowIcon(app_icon())

    apply_theme(
        app,
        theme_name=settings.get_theme(),
        accent_override=settings.get_accent() or None,
        font_size=settings.get_font_size(),
    )

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())