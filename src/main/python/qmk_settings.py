# SPDX-License-Identifier: GPL-2.0-or-later
import json
import struct

from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QGridLayout, QLabel, QWidget, QSizePolicy, QTabWidget, QSpinBox, \
    QHBoxLayout, QPushButton

from basic_editor import BasicEditor
from util import tr
from vial_device import VialKeyboard


class GenericOption:

    def __init__(self, option, container):
        self.row = container.rowCount()
        self.option = option
        self.qsid = self.option["qsid"]
        self.container = container

        self.container.addWidget(QLabel(option["title"]), self.row, 0)

    def reload(self, keyboard):
        data = keyboard.qmk_settings_get(self.qsid)
        if not data:
            raise RuntimeError("failed to retrieve setting {} from keyboard".format(self.option))
        return data


class BooleanOption(GenericOption):

    def __init__(self, option, container):
        super().__init__(option, container)

        self.qsid_bit = self.option["bit"]

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.on_change)
        self.container.addWidget(self.checkbox, self.row, 1)

    def on_change(self):
        print(self.option, self.checkbox.isChecked())

    def reload(self, keyboard):
        data = super().reload(keyboard)
        checked = data[0] & (1 << self.qsid_bit)

        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(checked != 0)
        self.checkbox.blockSignals(False)


class IntegerOption(GenericOption):

    def __init__(self, option, container):
        super().__init__(option, container)

        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(option["min"])
        self.spinbox.setMaximum(option["max"])
        self.container.addWidget(self.spinbox, self.row, 1)

    def reload(self, keyboard):
        data = super().reload(keyboard)[0:self.option["width"]]
        self.spinbox.setValue(int.from_bytes(data, byteorder="little"))


class QmkSettings(BasicEditor):

    def __init__(self, appctx):
        super().__init__()
        self.appctx = appctx
        self.keyboard = None

        self.tabs_widget = QTabWidget()
        self.addWidget(self.tabs_widget)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(QPushButton(tr("QmkSettings", "Save")))
        btn_undo = QPushButton(tr("QmkSettings", "Undo"))
        btn_undo.clicked.connect(self.reload_settings)
        buttons.addWidget(btn_undo)
        buttons.addWidget(QPushButton(tr("QmkSettings", "Reset")))
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

    def reload_settings(self):
        for tab in self.tabs:
            for field in tab:
                field.reload(self.keyboard)

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.reload_settings()

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard and self.device.keyboard.vial_protocol >= 3)  # TODO(xyz): protocol bump
