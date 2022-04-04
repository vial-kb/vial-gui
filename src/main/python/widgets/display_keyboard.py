# SPDX-License-Identifier: GPL-2.0-or-later
import json

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QWidget, QSizePolicy

from constants import KEYCODE_BTN_RATIO
from keycodes import Keycode
from util import KeycodeDisplay
from widgets.square_button import SquareButton
from kle_serial import Serial as KleSerial


class DisplayKeyboard(QWidget):

    keycode_changed = pyqtSignal(int)

    def __init__(self, kbdef):
        super().__init__()

        self.layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.buttons = []

        keymap = KleSerial().deserialize(json.loads(kbdef))
        for key in keymap.keys:
            kc = Keycode.find_by_qmk_id(key.labels[0])
            btn = SquareButton()
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setRelSize(KEYCODE_BTN_RATIO)
            btn.setContentsMargins(0, 0, 0, 0)
            btn.setToolTip(Keycode.tooltip(kc.code))
            btn.setText(kc.label)
            btn.clicked.connect(lambda st, k=kc: self.keycode_changed.emit(k.code))
            btn.keycode = kc

            self.buttons.append(btn)
            self.layout.addWidget(btn, round(key.y * 4), round(key.x * 4), round(key.height * 4), round(key.width * 4))

        self.setLayout(self.layout)

    def relabel_buttons(self):
        KeycodeDisplay.relabel_buttons(self.buttons)
