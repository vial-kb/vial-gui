# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLineEdit, QLabel

from keycodes import Keycode
from util import tr


class AnyKeycodeDialog(QDialog):

    def __init__(self, initial):
        super().__init__()

        self.setWindowTitle(tr("AnyKeycodeDialog", "Enter an arbitrary keycode"))

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.lbl_computed = QLabel()
        self.txt_entry = QLineEdit()
        self.txt_entry.textChanged.connect(self.on_change)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.txt_entry)
        self.layout.addWidget(self.lbl_computed)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

        self.value = initial
        ser = Keycode.serialize(initial)
        if isinstance(ser, int):
            ser = hex(ser)
        self.txt_entry.setText(ser)
        self.txt_entry.selectAll()
        self.on_change()

    def on_change(self):
        text = self.txt_entry.text()
        value = err = None
        try:
            value = Keycode.deserialize(text, reraise=True)
        except Exception as e:
            err = str(e)

        if not text:
            self.value = -1
            self.lbl_computed.setText(tr("AnyKeycodeDialog", "Enter an expression"))
        elif err:
            self.value = -1
            self.lbl_computed.setText(tr("AnyKeycodeDialog", "Invalid input: {}").format(err))
        elif isinstance(value, int):
            self.value = value
            self.lbl_computed.setText(tr("AnyKeycodeDialog", "Computed value: 0x{:X}").format(value))
        else:
            self.value = -1
            self.lbl_computed.setText(tr("AnyKeycodeDialog", "Invalid input"))

        self.buttons.button(QDialogButtonBox.Ok).setEnabled(0 <= self.value < 2 ** 16)
