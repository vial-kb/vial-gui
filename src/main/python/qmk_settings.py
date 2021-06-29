# SPDX-License-Identifier: GPL-2.0-or-later
import struct

from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QGridLayout, QLabel, QWidget, QSizePolicy

from basic_editor import BasicEditor
from vial_device import VialKeyboard


class QmkSettings(BasicEditor):

    def __init__(self):
        super().__init__()

        w = QWidget()
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.container = QGridLayout()
        w.setLayout(self.container)
        self.addWidget(w)
        self.setAlignment(w, QtCore.Qt.AlignHCenter)

        self.container.addWidget(QLabel("Always send Escape if Alt is pressed"), 0, 0)
        self.container.addWidget(QCheckBox(), 0, 1)
        self.container.addWidget(QLabel("Always send Escape if Control is pressed"), 1, 0)
        self.chk_ctrl = QCheckBox()
        self.chk_ctrl.stateChanged.connect(self.on_checked)
        self.container.addWidget(self.chk_ctrl, 1, 1)
        self.container.addWidget(QLabel("Always send Escape if GUI is pressed"), 2, 0)
        self.container.addWidget(QCheckBox(), 2, 1)
        self.container.addWidget(QLabel("Always send Escape if Shift is pressed"), 3, 0)
        self.container.addWidget(QCheckBox(), 3, 1)

        self.keyboard = None

    def reload_settings(self):
        gresc = self.keyboard.qmk_settings_get(1)[0]
        self.chk_ctrl.setChecked(gresc & 2)

    def on_checked(self, state):
        data = struct.pack("B", int(self.chk_ctrl.isChecked()) * 2)
        self.keyboard.qmk_settings_set(1, data)

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.reload_settings()

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard and self.device.keyboard.vial_protocol >= 3)  # TODO(xyz): protocol bump
