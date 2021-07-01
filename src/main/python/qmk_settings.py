# SPDX-License-Identifier: GPL-2.0-or-later
import json
from collections import defaultdict

from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QCheckBox, QGridLayout, QLabel, QWidget, QSizePolicy, QTabWidget, QSpinBox, \
    QHBoxLayout, QPushButton, QMessageBox

from basic_editor import BasicEditor
from util import tr
from vial_device import VialKeyboard


class GenericOption:

    def __init__(self, option, container):
        self.row = container.rowCount()
        self.option = option
        self.qsid = self.option["qsid"]
        self.container = container

        self.lbl = QLabel(option["title"])
        self.container.addWidget(self.lbl, self.row, 0)

    def reload(self, keyboard):
        data = keyboard.qmk_settings_get(self.qsid)
        if not data:
            raise RuntimeError("failed to retrieve setting {} from keyboard".format(self.option))
        return data

    def delete(self):
        self.lbl.hide()
        self.lbl.deleteLater()


class BooleanOption(GenericOption):

    def __init__(self, option, container):
        super().__init__(option, container)

        self.qsid_bit = self.option["bit"]

        self.checkbox = QCheckBox()
        self.container.addWidget(self.checkbox, self.row, 1)

    def reload(self, keyboard):
        data = super().reload(keyboard)
        checked = data[0] & (1 << self.qsid_bit)

        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(checked != 0)
        self.checkbox.blockSignals(False)

    def value(self):
        checked = int(self.checkbox.isChecked())
        return checked << self.qsid_bit

    def delete(self):
        super().delete()
        self.checkbox.hide()
        self.checkbox.deleteLater()


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

    def value(self):
        return self.spinbox.value().to_bytes(self.option["width"], byteorder="little")

    def delete(self):
        super().delete()
        self.spinbox.hide()
        self.spinbox.deleteLater()


class QmkSettings(BasicEditor):

    def __init__(self, appctx):
        super().__init__()
        self.appctx = appctx
        self.keyboard = None

        self.tabs_widget = QTabWidget()
        self.addWidget(self.tabs_widget)
        buttons = QHBoxLayout()
        buttons.addStretch()
        btn_save = QPushButton(tr("QmkSettings", "Save"))
        btn_save.clicked.connect(self.save_settings)
        buttons.addWidget(btn_save)
        btn_undo = QPushButton(tr("QmkSettings", "Undo"))
        btn_undo.clicked.connect(self.reload_settings)
        buttons.addWidget(btn_undo)
        btn_reset = QPushButton(tr("QmkSettings", "Reset"))
        btn_reset.clicked.connect(self.reset_settings)
        buttons.addWidget(btn_reset)
        self.addLayout(buttons)

        self.supported_settings = set()
        self.tabs = []
        self.misc_widgets = []

    def populate_tab(self, tab, container):
        options = []
        for field in tab["fields"]:
            if field["qsid"] not in self.supported_settings:
                continue
            if field["type"] == "boolean":
                options.append(BooleanOption(field, container))
            elif field["type"] == "integer":
                options.append(IntegerOption(field, container))
            else:
                raise RuntimeError("unsupported field type: {}".format(field))
        return options

    def recreate_gui(self):
        # delete old GUI
        for tab in self.tabs:
            for field in tab:
                field.delete()
        self.tabs.clear()
        for w in self.misc_widgets:
            w.hide()
            w.deleteLater()
        self.misc_widgets.clear()
        while self.tabs_widget.count() > 0:
            self.tabs_widget.removeTab(0)

        with open(self.appctx.get_resource("qmk_settings.json"), "r") as inf:
            settings = json.load(inf)

        # create new GUI
        for tab in settings["tabs"]:
            # don't bother creating tabs that would be empty - i.e. at least one qsid in a tab should be supported
            use_tab = False
            for field in tab["fields"]:
                if field["qsid"] in self.supported_settings:
                    use_tab = True
                    break
            if not use_tab:
                continue

            w = QWidget()
            w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
            container = QGridLayout()
            w.setLayout(container)
            l = QVBoxLayout()
            l.addWidget(w)
            l.setAlignment(w, QtCore.Qt.AlignHCenter)
            w2 = QWidget()
            w2.setLayout(l)
            self.misc_widgets += [w, w2]
            self.tabs_widget.addTab(w2, tab["name"])
            self.tabs.append(self.populate_tab(tab, container))

    def reload_settings(self):
        self.supported_settings = set(self.keyboard.qmk_settings_query())
        self.recreate_gui()

        for tab in self.tabs:
            for field in tab:
                field.reload(self.keyboard)

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.reload_settings()

    def save_settings(self):
        qsid_values = defaultdict(int)
        for tab in self.tabs:
            for field in tab:
                # hack for boolean options - we pack several booleans into a single byte
                if isinstance(field, BooleanOption):
                    qsid_values[field.qsid] |= field.value()
                else:
                    qsid_values[field.qsid] = field.value()

        for qsid, value in qsid_values.items():
            if isinstance(value, int):
                value = value.to_bytes(1, byteorder="little")
            self.keyboard.qmk_settings_set(qsid, value)

    def reset_settings(self):
        if QMessageBox.question(self.widget(), "",
                                tr("QmkSettings", "Reset all settings to default values?"),
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.keyboard.qmk_settings_reset()
            self.reload_settings()

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard and self.device.keyboard.vial_protocol >= 3)  # TODO(xyz): protocol bump
