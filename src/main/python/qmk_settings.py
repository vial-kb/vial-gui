# SPDX-License-Identifier: GPL-2.0-or-later
import json
import struct

from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QGridLayout, QLabel, QWidget, QSizePolicy, QTabWidget, QSpinBox, \
    QHBoxLayout, QPushButton

from basic_editor import BasicEditor
from vial_device import VialKeyboard


class GenericOption:

    def __init__(self, option, container):
        self.row = container.rowCount()
        self.option = option
        self.container = container

        self.container.addWidget(QLabel(option["title"]), self.row, 0)


class BooleanOption(GenericOption):

    def __init__(self, option, container):
        super().__init__(option, container)

        self.checkbox = QCheckBox()
        self.container.addWidget(self.checkbox, self.row, 1)


class IntegerOption(GenericOption):

    def __init__(self, option ,container):
        super().__init__(option, container)

        self.spinbox = QSpinBox()
        self.container.addWidget(self.spinbox, self.row, 1)


class QmkSettings(BasicEditor):

    def __init__(self, appctx):
        super().__init__()
        self.appctx = appctx
        self.keyboard = None

        self.tabs_widget = QTabWidget()
        self.addWidget(self.tabs_widget)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(QPushButton("Save"))
        buttons.addWidget(QPushButton("Undo"))
        buttons.addWidget(QPushButton("Reset"))
        self.addLayout(buttons)

        self.tabs = []
        self.create_gui()

    @staticmethod
    def populate_tab(tab, container):
        options = []
        for field in tab["fields"]:
            if field["type"] == "boolean":
                options.append(BooleanOption(field, container))
            elif field["type"] == "integer":
                options.append(IntegerOption(field, container))
            else:
                raise RuntimeError("unsupported field type: {}".format(field))
        return options

    def create_gui(self):
        with open(self.appctx.get_resource("qmk_settings.json"), "r") as inf:
            settings = json.load(inf)

        for tab in settings["tabs"]:
            w = QWidget()
            w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            container = QGridLayout()
            w.setLayout(container)
            l = QVBoxLayout()
            l.addWidget(w)
            l.setAlignment(w, QtCore.Qt.AlignHCenter)
            w2 = QWidget()
            w2.setLayout(l)
            self.tabs_widget.addTab(w2, tab["name"])
            self.tabs.append(self.populate_tab(tab, container))

        # self.container.addWidget(QLabel("Always send Escape if Alt is pressed"), 0, 0)
        # self.container.addWidget(QCheckBox(), 0, 1)
        # self.container.addWidget(QLabel("Always send Escape if Control is pressed"), 1, 0)
        # self.chk_ctrl = QCheckBox()
        # self.chk_ctrl.stateChanged.connect(self.on_checked)
        # self.container.addWidget(self.chk_ctrl, 1, 1)
        # self.container.addWidget(QLabel("Always send Escape if GUI is pressed"), 2, 0)
        # self.container.addWidget(QCheckBox(), 2, 1)
        # self.container.addWidget(QLabel("Always send Escape if Shift is pressed"), 3, 0)
        # self.container.addWidget(QCheckBox(), 3, 1)

    def reload_settings(self):
        gresc = self.keyboard.qmk_settings_get(1)[0]
        # self.chk_ctrl.setChecked(gresc & 2)

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
