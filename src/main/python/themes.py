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


nord_palette = QPalette()
nord_palette.setColor(QPalette.Window, QColor("#2e3440"))
nord_palette.setColor(QPalette.WindowText, QColor("#eceff4"))
nord_palette.setColor(QPalette.Base, QColor("#2e3440"))
nord_palette.setColor(QPalette.AlternateBase, QColor("#434c5e"))
nord_palette.setColor(QPalette.ToolTipBase, QColor("#4c566a"))
nord_palette.setColor(QPalette.ToolTipText, QColor("#eceff4"))
nord_palette.setColor(QPalette.Text, QColor("#eceff4"))
nord_palette.setColor(QPalette.Button, QColor("#2e3440"))
nord_palette.setColor(QPalette.ButtonText, QColor("#eceff4"))
nord_palette.setColor(QPalette.BrightText, QColor("#88c0d0"))
nord_palette.setColor(QPalette.Link, QColor("#88c0d0"))
nord_palette.setColor(QPalette.Highlight, QColor("#88c0d0"))
nord_palette.setColor(QPalette.HighlightedText, QColor("#eceff4"))
nord_palette.setColor(QPalette.Active, QPalette.Button, QColor("#2e3440"))
nord_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#eceff4"))
nord_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#eceff4"))
nord_palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#eceff4"))
nord_palette.setColor(QPalette.Disabled, QPalette.Light, QColor("#88c0d0"))


olivial_palette = QPalette()
olivial_palette.setColor(QPalette.Window, QColor("#181818"))
olivial_palette.setColor(QPalette.WindowText, QColor("#d9d9d9"))
olivial_palette.setColor(QPalette.Base, QColor("#181818"))
olivial_palette.setColor(QPalette.AlternateBase, QColor("#2c2c2c"))
olivial_palette.setColor(QPalette.ToolTipBase, QColor("#363636 "))
olivial_palette.setColor(QPalette.ToolTipText, QColor("#d9d9d9"))
olivial_palette.setColor(QPalette.Text, QColor("#d9d9d9"))
olivial_palette.setColor(QPalette.Button, QColor("#181818"))
olivial_palette.setColor(QPalette.ButtonText, QColor("#d9d9d9"))
olivial_palette.setColor(QPalette.BrightText, QColor("#fabcad"))
olivial_palette.setColor(QPalette.Link, QColor("#fabcad"))
olivial_palette.setColor(QPalette.Highlight, QColor("#fabcad"))
olivial_palette.setColor(QPalette.HighlightedText, QColor("#2c2c2c"))
olivial_palette.setColor(QPalette.Active, QPalette.Button, QColor("#181818"))
olivial_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#d9d9d9"))
olivial_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#d9d9d9"))
olivial_palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#d9d9d9"))
olivial_palette.setColor(QPalette.Disabled, QPalette.Light, QColor("#fabcad"))

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
    elif theme == "nord":
        QApplication.setPalette(nord_palette)
        QApplication.setStyle("Fusion")
    elif theme == "olivial":
        QApplication.setPalette(olivial_palette)
        QApplication.setStyle("Fusion")
    # For default/system theme, do nothing
    # User will have to restart the application for it to be applied
