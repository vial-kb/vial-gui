# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTabWidget, QWidget, QSizePolicy, QGridLayout, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, \
    QPushButton

from util import tr
from vial_device import VialKeyboard
from basic_editor import BasicEditor


class TapDance(BasicEditor):

    def __init__(self):
        super().__init__()
        self.keyboard = None

        self.tabs = QTabWidget()
        for x in range(32):
            container = QGridLayout()

            container.addWidget(QLabel("On tap"), 0, 0)
            container.addWidget(QLineEdit(), 0, 1)
            container.addWidget(QLabel("On hold"), 1, 0)
            container.addWidget(QLineEdit(), 1, 1)
            container.addWidget(QLabel("On double tap"), 2, 0)
            container.addWidget(QLineEdit(), 2, 1)
            container.addWidget(QLabel("On tap + hold"), 3, 0)
            container.addWidget(QLineEdit(), 3, 1)

            w = QWidget()
            w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            w.setLayout(container)
            l = QVBoxLayout()
            l.addStretch()
            l.addWidget(w)
            l.setAlignment(w, QtCore.Qt.AlignHCenter)
            l.addSpacing(100)
            lbl = QLabel("Use <code>TD({})</code> to set up this action in the keymap.".format(x))
            l.addWidget(lbl)
            l.setAlignment(lbl, QtCore.Qt.AlignHCenter)
            l.addStretch()
            w2 = QWidget()
            w2.setLayout(l)
            self.tabs.addTab(w2, str(x))

        self.addWidget(self.tabs)
        buttons = QHBoxLayout()
        buttons.addStretch()
        btn_save = QPushButton(tr("TapDance", "Save"))
        btn_revert = QPushButton(tr("TapDance", "Revert"))
        buttons.addWidget(btn_save)
        buttons.addWidget(btn_revert)
        self.addLayout(buttons)

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard and self.device.keyboard.vial_protocol >= 4)
