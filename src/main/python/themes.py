# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor

dark_palette = QPalette()
dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
dark_palette.setColor(QPalette.WindowText, Qt.white)
dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
dark_palette.setColor(QPalette.ToolTipText, Qt.white)
dark_palette.setColor(QPalette.Text, Qt.white)
dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
dark_palette.setColor(QPalette.ButtonText, Qt.white)
dark_palette.setColor(QPalette.BrightText, Qt.red)
dark_palette.setColor(QPalette.Link, QColor(247, 169, 72))
dark_palette.setColor(QPalette.Highlight, QColor(186, 186, 186))
dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
dark_palette.setColor(QPalette.Active, QPalette.Button, QColor(53, 53, 53))
dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.darkGray)
dark_palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
dark_palette.setColor(QPalette.Disabled, QPalette.Light, QColor(53, 53, 53))

arc_palette = QPalette()
arc_palette.setColor(QPalette.Window, QColor("#353945"))
arc_palette.setColor(QPalette.WindowText, QColor("#d3dae3"))
arc_palette.setColor(QPalette.Base, QColor("#353945"))
arc_palette.setColor(QPalette.AlternateBase, QColor("#404552"))
arc_palette.setColor(QPalette.ToolTipBase, QColor("#4B5162"))
arc_palette.setColor(QPalette.ToolTipText, QColor("#d3dae3"))
arc_palette.setColor(QPalette.Text, QColor("#d3dae3"))
arc_palette.setColor(QPalette.Button, QColor("#353945"))
arc_palette.setColor(QPalette.ButtonText, QColor("#d3dae3"))
arc_palette.setColor(QPalette.BrightText, QColor("#5294e2"))
arc_palette.setColor(QPalette.Link, QColor("#89b1e0"))
arc_palette.setColor(QPalette.Highlight, QColor("#5294e2"))
arc_palette.setColor(QPalette.HighlightedText, QColor("#d3dae3"))
arc_palette.setColor(QPalette.Active, QPalette.Button, QColor("#353945"))
arc_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#d3dae3"))
arc_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#d3dae3"))
arc_palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#d3dae3"))
arc_palette.setColor(QPalette.Disabled, QPalette.Light, QColor("#404552"))


def set_theme(theme):
    if theme == "light":
        QApplication.setPalette(QApplication.style().standardPalette())
        QApplication.setStyle("Fusion")
    elif theme == "dark":
        QApplication.setPalette(dark_palette)
        QApplication.setStyle("Fusion")
    elif theme == "arc":
        QApplication.setPalette(arc_palette)
        QApplication.setStyle("Fusion")
    else:
        QApplication.setPalette(QApplication.style().standardPalette())
        QApplication.setStyle(None)
