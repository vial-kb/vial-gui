# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5.QtWidgets import QTabWidget

from tabbed_keycodes import TabbedKeycodes


class TabWidgetWithKeycodes(QTabWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentChanged.connect(self.on_changed)

    def mouseReleaseEvent(self, ev):
        TabbedKeycodes.close_tray()

    def on_changed(self, index):
        TabbedKeycodes.close_tray()
