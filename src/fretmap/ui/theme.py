"""Темы приложения."""

from __future__ import annotations


THEMES: dict[str, dict[str, str]] = {
    "graphite": {
        "bg": "#1e1e22",
        "surface": "#2a2a30",
        "surface_2": "#34343c",
        "workspace": "#101014",
        "border": "#3d3d46",
        "text": "#e6e6e8",
        "text_dim": "#9a9aa2",
        "accent": "#5c2a37",
        "accent_hover": "#703542",
        "accent_press": "#472028",
        "accent_text": "#e6e6e8",
    },
    "wine": {
        "bg": "#201418",
        "surface": "#2e1e24",
        "surface_2": "#3a262e",
        "workspace": "#120a0d",
        "border": "#4a2e37",
        "text": "#f0e0e4",
        "text_dim": "#b098a0",
        "accent": "#7a2538",
        "accent_hover": "#8f2f45",
        "accent_press": "#5c1a2a",
        "accent_text": "#f0e0e4",
    },
    "nord": {
        "bg": "#2e3440",
        "surface": "#3b4252",
        "surface_2": "#434c5e",
        "workspace": "#1e222a",
        "border": "#4c566a",
        "text": "#eceff4",
        "text_dim": "#a0a8b8",
        "accent": "#5e81ac",
        "accent_hover": "#6f92bd",
        "accent_press": "#4c6f9a",
        "accent_text": "#eceff4",
    },
    "solarized_dark": {
        "bg": "#002b36",
        "surface": "#073642",
        "surface_2": "#0e4250",
        "workspace": "#001820",
        "border": "#1a4a58",
        "text": "#eee8d5",
        "text_dim": "#93a1a1",
        "accent": "#b58900",
        "accent_hover": "#c99a10",
        "accent_press": "#9a7400",
        "accent_text": "#002b36",
    },
    "light": {
        "bg": "#f4f4f6",
        "surface": "#ffffff",
        "surface_2": "#ececf0",
        "workspace": "#d8d8dc",
        "border": "#c8c8d0",
        "text": "#1e1e22",
        "text_dim": "#6a6a72",
        "accent": "#8f2532",
        "accent_hover": "#a03040",
        "accent_press": "#701a24",
        "accent_text": "#ffffff",
    },
}

DEFAULT_THEME = "nord"


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*[max(0, min(255, c)) for c in rgb])


def _lighten(color: str, amount: float) -> str:
    r, g, b = _hex_to_rgb(color)
    return _rgb_to_hex((
        int(r + (255 - r) * amount),
        int(g + (255 - g) * amount),
        int(b + (255 - b) * amount),
    ))


def _darken(color: str, amount: float) -> str:
    r, g, b = _hex_to_rgb(color)
    return _rgb_to_hex((
        int(r * (1 - amount)),
        int(g * (1 - amount)),
        int(b * (1 - amount)),
    ))


def get_palette(name: str, accent_override: str | None = None) -> dict[str, str]:
    palette = dict(THEMES.get(name, THEMES[DEFAULT_THEME]))
    if accent_override:
        palette["accent"] = accent_override
        palette["accent_hover"] = _lighten(accent_override, 0.15)
        palette["accent_press"] = _darken(accent_override, 0.15)
    return palette


def build_stylesheet(palette: dict[str, str], font_size: int = 10) -> str:
    bg = palette["bg"]
    surface = palette["surface"]
    surface_2 = palette["surface_2"]
    workspace = palette["workspace"]
    border = palette["border"]
    text = palette["text"]
    text_dim = palette["text_dim"]
    accent = palette["accent"]
    accent_hover = palette["accent_hover"]
    accent_press = palette["accent_press"]
    accent_text = palette["accent_text"]

    return f"""
QWidget {{
    background-color: {bg};
    color: {text};
    font-size: {font_size}pt;
}}

QMainWindow, QDialog {{
    background-color: {bg};
}}

QStackedWidget {{
    background-color: {bg};
}}

QMenuBar {{
    background-color: {surface};
    color: {text};
    border-bottom: 1px solid {border};
}}
QMenuBar::item {{
    padding: 6px 12px;
    background: transparent;
}}
QMenuBar::item:selected {{
    background-color: {accent};
    color: {accent_text};
}}
QMenu {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
}}
QMenu::item {{
    padding: 6px 24px 6px 24px;
}}
QMenu::item:selected {{
    background-color: {accent};
    color: {accent_text};
}}

QLineEdit, QComboBox, QSpinBox {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 5px 8px;
    selection-background-color: {accent};
    selection-color: {accent_text};
    min-height: 20px;
}}
QLineEdit:focus, QComboBox:focus {{
    border: 1px solid {accent};
}}
QLineEdit:disabled, QComboBox:disabled {{
    color: {text_dim};
    background-color: {bg};
}}
QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox QAbstractItemView {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    selection-background-color: {accent};
    selection-color: {accent_text};
}}

QPushButton, QToolButton {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 4px;
    padding: 6px 12px;
    min-height: 20px;
}}
QPushButton:hover, QToolButton:hover {{
    background-color: {surface_2};
    border: 1px solid {accent};
}}
QPushButton:pressed, QToolButton:pressed {{
    background-color: {accent_press};
}}
QPushButton:disabled, QToolButton:disabled {{
    color: {text_dim};
    background-color: {bg};
    border: 1px solid {border};
}}

QPushButton#primary {{
    background-color: {accent};
    color: {accent_text};
    border: 1px solid {accent};
    font-weight: bold;
}}
QPushButton#primary:hover {{
    background-color: {accent_hover};
}}
QPushButton#primary:pressed {{
    background-color: {accent_press};
}}

QPushButton#launcherButton {{
    background-color: {surface};
    color: {text};
    border: 2px solid {accent};
    border-radius: 8px;
    font-size: {font_size + 4}pt;
    font-weight: bold;
    padding: 20px;
}}
QPushButton#launcherButton:hover {{
    background-color: {surface_2};
    border: 2px solid {accent_hover};
}}
QPushButton#launcherButton:pressed {{
    background-color: {accent_press};
    color: {accent_text};
}}

QPushButton#launcherButtonDisabled {{
    background-color: {bg};
    color: {text_dim};
    border: 2px dashed {border};
    border-radius: 8px;
    font-size: {font_size + 4}pt;
    font-weight: bold;
    padding: 20px;
}}
QPushButton#launcherButtonDisabled:disabled {{
    color: {text_dim};
    background-color: {bg};
}}

QScrollArea#workspace {{
    background-color: {workspace};
    border: 1px solid {border};
    border-radius: 6px;
}}
QScrollArea#workspace > QWidget > QWidget {{
    background-color: {workspace};
}}

QFrame#card {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 6px;
}}
QFrame#card:hover {{
    border: 1px solid {accent};
}}

QPushButton#cardClose {{
    background-color: transparent;
    color: {text_dim};
    border: none;
    font-size: 16pt;
    font-weight: bold;
    padding: 0;
    border-radius: 13px;
}}
QPushButton#cardClose:hover {{
    background-color: {accent};
    color: {accent_text};
}}
QPushButton#cardClose:pressed {{
    background-color: {accent_press};
    color: {accent_text};
}}

QLabel#dragHandle {{
    color: {text_dim};
    font-size: 14pt;
    font-weight: bold;
    padding: 2px 8px;
    background: transparent;
}}
QLabel#dragHandle:hover {{
    color: {accent};
}}

QLabel#fieldLabel {{
    color: {text_dim};
    padding: 0 2px;
}}

QLabel#status {{
    color: {text_dim};
    padding: 4px 6px;
}}

QLabel#topTitle {{
    color: {text};
    font-size: {font_size + 3}pt;
    font-weight: bold;
    padding: 4px 0;
}}

QLabel#workspaceHint {{
    color: {text_dim};
    font-size: {font_size + 1}pt;
    padding: 40px;
}}

QScrollBar:vertical, QScrollBar:horizontal {{
    background: {bg};
    border: none;
    width: 12px;
    height: 12px;
}}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background: {border};
    border-radius: 6px;
    min-height: 24px;
    min-width: 24px;
}}
QScrollBar::handle:hover {{
    background: {accent};
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    background: none;
    height: 0;
    width: 0;
}}
QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
}}

QSlider::groove:horizontal {{
    background: {border};
    height: 6px;
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {accent};
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}
QSlider::handle:horizontal:hover {{
    background: {accent_hover};
}}

QToolTip {{
    background-color: {surface_2};
    color: {text};
    border: 1px solid {accent};
    padding: 4px 6px;
}}
"""


def apply_theme(
    app,
    theme_name: str = DEFAULT_THEME,
    accent_override: str | None = None,
    font_size: int = 10,
) -> None:
    palette = get_palette(theme_name, accent_override)
    app.setStyleSheet("")
    app.setStyleSheet(build_stylesheet(palette, font_size))