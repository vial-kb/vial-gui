# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor

themes = [
    ("Light", {
        QPalette.Window: "#ffefebe7",
        QPalette.WindowText: "#ff000000",
        QPalette.Base: "#ffffffff",
        QPalette.AlternateBase: "#fff7f5f3",
        QPalette.ToolTipBase: "#ffffffdc",
        QPalette.ToolTipText: "#ff000000",
        QPalette.Text: "#ff000000",
        QPalette.Button: "#ffefebe7",
        QPalette.ButtonText: "#ff000000",
        QPalette.BrightText: "#ffffffff",
        QPalette.Link: "#ff0000ff",
        QPalette.Highlight: "#ff308cc6",
        QPalette.HighlightedText: "#ffffffff",
        (QPalette.Active, QPalette.Button): "#ffefebe7",
        (QPalette.Disabled, QPalette.ButtonText): "#ffbebebe",
        (QPalette.Disabled, QPalette.WindowText): "#ffbebebe",
        (QPalette.Disabled, QPalette.Text): "#ffbebebe",
        (QPalette.Disabled, QPalette.Light): "#ffffffff",
    }),
    ("Dark", {
        QPalette.Window: "#353535",
        QPalette.WindowText: "#ffffff",
        QPalette.Base: "#232323",
        QPalette.AlternateBase: "#353535",
        QPalette.ToolTipBase: "#191919",
        QPalette.ToolTipText: "#ffffff",
        QPalette.Text: "#ffffff",
        QPalette.Button: "#353535",
        QPalette.ButtonText: "#ffffff",
        QPalette.BrightText: "#ff0000",
        QPalette.Link: "#f7a948",
        QPalette.Highlight: "#bababa",
        QPalette.HighlightedText: "#232323",
        (QPalette.Active, QPalette.Button): "#353535",
        (QPalette.Disabled, QPalette.ButtonText): "#808080",
        (QPalette.Disabled, QPalette.WindowText): "#808080",
        (QPalette.Disabled, QPalette.Text): "#808080",
        (QPalette.Disabled, QPalette.Light): "#353535",
    }),
    ("Arc", {
        QPalette.Window: "#353945",
        QPalette.WindowText: "#d3dae3",
        QPalette.Base: "#353945",
        QPalette.AlternateBase: "#404552",
        QPalette.ToolTipBase: "#4B5162",
        QPalette.ToolTipText: "#d3dae3",
        QPalette.Text: "#d3dae3",
        QPalette.Button: "#353945",
        QPalette.ButtonText: "#d3dae3",
        QPalette.BrightText: "#5294e2",
        QPalette.Link: "#89b1e0",
        QPalette.Highlight: "#5294e2",
        QPalette.HighlightedText: "#d3dae3",
        (QPalette.Active, QPalette.Button): "#353945",
        (QPalette.Disabled, QPalette.ButtonText): "#d3dae3",
        (QPalette.Disabled, QPalette.WindowText): "#d3dae3",
        (QPalette.Disabled, QPalette.Text): "#d3dae3",
        (QPalette.Disabled, QPalette.Light): "#404552",
    }),
    ("Nord", {
        QPalette.Window: "#2e3440",
        QPalette.WindowText: "#eceff4",
        QPalette.Base: "#2e3440",
        QPalette.AlternateBase: "#434c5e",
        QPalette.ToolTipBase: "#4c566a",
        QPalette.ToolTipText: "#eceff4",
        QPalette.Text: "#eceff4",
        QPalette.Button: "#2e3440",
        QPalette.ButtonText: "#eceff4",
        QPalette.BrightText: "#88c0d0",
        QPalette.Link: "#88c0d0",
        QPalette.Highlight: "#88c0d0",
        QPalette.HighlightedText: "#eceff4",
        (QPalette.Active, QPalette.Button): "#2e3440",
        (QPalette.Disabled, QPalette.ButtonText): "#eceff4",
        (QPalette.Disabled, QPalette.WindowText): "#eceff4",
        (QPalette.Disabled, QPalette.Text): "#eceff4",
        (QPalette.Disabled, QPalette.Light): "#88c0d0",
    }),
    ("Olivia", {
        QPalette.Window: "#181818",
        QPalette.WindowText: "#d9d9d9",
        QPalette.Base: "#181818",
        QPalette.AlternateBase: "#2c2c2c",
        QPalette.ToolTipBase: "#363636 ",
        QPalette.ToolTipText: "#d9d9d9",
        QPalette.Text: "#d9d9d9",
        QPalette.Button: "#181818",
        QPalette.ButtonText: "#d9d9d9",
        QPalette.BrightText: "#fabcad",
        QPalette.Link: "#fabcad",
        QPalette.Highlight: "#fabcad",
        QPalette.HighlightedText: "#2c2c2c",
        (QPalette.Active, QPalette.Button): "#181818",
        (QPalette.Disabled, QPalette.ButtonText): "#d9d9d9",
        (QPalette.Disabled, QPalette.WindowText): "#d9d9d9",
        (QPalette.Disabled, QPalette.Text): "#d9d9d9",
        (QPalette.Disabled, QPalette.Light): "#fabcad",
    }),
    ("Dracula", {
        QPalette.Window: "#282a36",
        QPalette.WindowText: "#f8f8f2",
        QPalette.Base: "#282a36",
        QPalette.AlternateBase: "#44475a",
        QPalette.ToolTipBase: "#6272a4",
        QPalette.ToolTipText: "#f8f8f2",
        QPalette.Text: "#f8f8f2",
        QPalette.Button: "#282a36",
        QPalette.ButtonText: "#f8f8f2",
        QPalette.BrightText: "#8be9fd",
        QPalette.Link: "#8be9fd",
        QPalette.Highlight: "#8be9fd",
        QPalette.HighlightedText: "#f8f8f2",
        (QPalette.Active, QPalette.Button): "#282a36",
        (QPalette.Disabled, QPalette.ButtonText): "#f8f8f2",
        (QPalette.Disabled, QPalette.WindowText): "#f8f8f2",
        (QPalette.Disabled, QPalette.Text): "#f8f8f2",
        (QPalette.Disabled, QPalette.Light): "#8be9fd",
    }),
    ("Bliss", {
        QPalette.Window: "#343434",
        QPalette.WindowText: "#cbc8c9",
        QPalette.Base: "#343434",
        QPalette.AlternateBase: "#3b3b3b",
        QPalette.ToolTipBase: "#424242",
        QPalette.ToolTipText: "#cbc8c9",
        QPalette.Text: "#cbc8c9",
        QPalette.Button: "#343434",
        QPalette.ButtonText: "#cbc8c9",
        QPalette.BrightText: "#f5d1c8",
        QPalette.Link: "#f5d1c8",
        QPalette.Highlight: "#f5d1c8",
        QPalette.HighlightedText: "#424242",
        (QPalette.Active, QPalette.Button): "#343434",
        (QPalette.Disabled, QPalette.ButtonText): "#cbc8c9",
        (QPalette.Disabled, QPalette.WindowText): "#cbc8c9",
        (QPalette.Disabled, QPalette.Text): "#cbc8c9",
        (QPalette.Disabled, QPalette.Light): "#f5d1c8",
    }),
]

palettes = dict()

for name, colors in themes:
    palette = QPalette()
    for role, color in colors.items():
        if not hasattr(type(role), '__iter__'):
            role = [role]
        palette.setColor(*role, QColor(color))
    palettes[name] = palette


class Theme:

    theme = ""

    @classmethod
    def set_theme(cls, theme):
        cls.theme = theme
        if theme in palettes:
            QApplication.setPalette(palettes[theme])
            QApplication.setStyle("Fusion")
        # For default/system theme, do nothing
        # User will have to restart the application for it to be applied

    @classmethod
    def get_theme(cls):
        return cls.theme

    @classmethod
    def mask_light_factor(cls):
        if cls.theme == "Light":
            return 103
        return 150
