# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel, QCheckBox, QComboBox, QGridLayout, QWidget, QSizePolicy

from basic_editor import BasicEditor
from vial_device import VialKeyboard


class BooleanChoice:

    def __init__(self, cb, container, label):
        self.cb = cb
        self.choice = False

        self.widget_label = QLabel(label)
        self.widget_checkbox = QCheckBox()
        self.widget_checkbox.stateChanged.connect(self.on_checkbox)

        row = container.rowCount()
        container.addWidget(self.widget_label, row, 0)
        container.addWidget(self.widget_checkbox, row, 1)

    def delete(self):
        self.widget_label.hide()
        self.widget_label.deleteLater()
        self.widget_checkbox.hide()
        self.widget_checkbox.deleteLater()

    def pack(self):
        return str(int(self.choice))

    def unpack(self, value):
        self.change(int(value))

    def change(self, value):
        self.choice = bool(value)
        self.widget_checkbox.setChecked(self.choice)

    def on_checkbox(self):
        self.choice = self.widget_checkbox.isChecked()
        self.cb()


class SelectChoice:

    def __init__(self, cb, container, label, options):
        self.cb = cb
        self.choice = 0
        self.options = options

        self.widget_label = QLabel(label)
        self.widget_options = QComboBox()
        self.widget_options.addItems(options)
        self.widget_options.currentIndexChanged.connect(self.on_selection)

        row = container.rowCount()
        container.addWidget(self.widget_label, row, 0)
        container.addWidget(self.widget_options, row, 1)

    def delete(self):
        self.widget_label.hide()
        self.widget_label.deleteLater()
        self.widget_options.hide()
        self.widget_options.deleteLater()

    def pack(self):
        val = bin(self.choice)[2:]
        val = "0" * ((len(self.options) - 1).bit_length() - len(val)) + val
        return val

    def unpack(self, value):
        self.change(int(value, 2))

    def change(self, value):
        self.choice = value
        self.widget_options.setCurrentIndex(self.choice)

    def on_selection(self):
        self.choice = self.widget_options.currentIndex()
        self.cb()


class LayoutEditor(BasicEditor):

    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.device = None

        self.choices = []

        self.widgets = []

        w = QWidget()
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.container = QGridLayout()
        w.setLayout(self.container)
        self.addWidget(w)
        self.setAlignment(w, QtCore.Qt.AlignHCenter)

    def rebuild(self, device):
        super().rebuild(device)

        if not self.valid():
            return

        self.blockSignals(True)

        for choice in self.choices:
            choice.delete()
        self.choices = []

        for item in device.keyboard.layout_labels:
            if isinstance(item, str):
                choice = BooleanChoice(self.on_changed, self.container, item)
            else:
                choice = SelectChoice(self.on_changed, self.container, item[0], item[1:])
            self.choices.append(choice)

        self.unpack(self.device.keyboard.layout_options)

        self.blockSignals(False)

    def valid(self):
        return isinstance(self.device, VialKeyboard) and self.device.keyboard.layout_labels

    def pack(self):
        if not self.choices:
            return 0
        val = ""
        for choice in self.choices:
            val += choice.pack()
        return int(val, 2)

    def unpack(self, value):
        # we operate on bit strings
        value = "0" * 100 + bin(value)[2:]

        # VIA stores option choices backwards, we need to parse the input in reverse
        for choice in self.choices[::-1]:
            sz = len(choice.pack())
            choice.unpack(value[-sz:])
            value = value[:-sz]

    def get_choice(self, index):
        return int(self.choices[index].pack(), 2)

    def on_changed(self):
        self.changed.emit()
