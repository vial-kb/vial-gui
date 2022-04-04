# SPDX-License-Identifier: GPL-2.0-or-later
import json

from PyQt5.QtWidgets import QGridLayout, QWidget, QSizePolicy

from constants import KEYCODE_BTN_RATIO
from keycodes import Keycode
from widgets.square_button import SquareButton
from kle_serial import Serial as KleSerial


class DisplayKeyboard(QWidget):

    def btn(self, kc):
        kc = Keycode.find_by_qmk_id(kc)

        btn = SquareButton()
        # btn.setWordWrap(self.word_wrap)
        btn.setRelSize(KEYCODE_BTN_RATIO)
        btn.setContentsMargins(0, 0, 0, 0)
        btn.setToolTip(Keycode.tooltip(kc.code))
        btn.setText(kc.label)
        # btn.clicked.connect(lambda st, k=keycode: self.keycode_changed.emit(k.code))
        btn.keycode = kc.code
        return btn

    def __init__(self, kbdef):
        super().__init__()

        self.layout = QGridLayout()
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        keymap = KleSerial().deserialize(json.loads(kbdef))
        for key in keymap.keys:
            self.layout.addWidget(self.btn(key.labels[0]),
                                  round(key.y * 4), round(key.x * 4),
                                  round(key.height * 4), round(key.width * 4))

        self.setLayout(self.layout)
