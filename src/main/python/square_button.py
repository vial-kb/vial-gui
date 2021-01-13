# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton

class SquareButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.scale = 1.2

    def setRelSize(self, ratio):
        self.scale = ratio
        self.updateGeometry()

    def sizeHint(self):
        size = int(round(self.fontMetrics().height() * self.scale))
        return QSize(size, size)
