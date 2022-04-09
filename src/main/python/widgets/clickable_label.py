# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, ev):
        self.clicked.emit()
