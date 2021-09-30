# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QSizePolicy, QGridLayout, QVBoxLayout, QLabel, QCheckBox

from key_widget import KeyWidget
from vial_device import VialKeyboard
from basic_editor import BasicEditor
from widgets.checkbox_no_padding import CheckBoxNoPadding
from widgets.tab_widget_keycodes import TabWidgetWithKeycodes


class ModsUI(QWidget):

    def __init__(self):
        super().__init__()

        container = QGridLayout()
        container.addWidget(CheckBoxNoPadding("LCtrl"), 0, 0)
        container.addWidget(CheckBoxNoPadding("RCtrl"), 1, 0)

        container.addWidget(CheckBoxNoPadding("LShift"), 0, 1)
        container.addWidget(CheckBoxNoPadding("RShift"), 1, 1)

        container.addWidget(CheckBoxNoPadding("LAlt"), 0, 2)
        container.addWidget(CheckBoxNoPadding("RAlt"), 1, 2)

        container.addWidget(CheckBoxNoPadding("LGui"), 0, 3)
        container.addWidget(CheckBoxNoPadding("RGui"), 1, 3)

        self.setLayout(container)


class KeyOverrideEntryUI(QObject):

    key_changed = pyqtSignal()

    def __init__(self, idx):
        super().__init__()

        self.idx = idx
        self.container = QGridLayout()
        self.populate_container()

        w = QWidget()
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        w.setLayout(self.container)
        l = QVBoxLayout()
        l.addWidget(w)
        l.setAlignment(w, QtCore.Qt.AlignHCenter)
        self.w2 = QWidget()
        self.w2.setLayout(l)

    def populate_container(self):
        self.container.addWidget(QLabel("Enable"), 0, 0)
        self.container.addWidget(QCheckBox(), 0, 1)

        self.container.addWidget(QLabel("Enable on layers"), 1, 0)
        layers_grid = QGridLayout()
        for x in range(8):
            layers_grid.addWidget(CheckBoxNoPadding(str(x)), 0, x)
            layers_grid.addWidget(CheckBoxNoPadding(str(8 + x)), 1, x)
        w = QWidget()
        w.setLayout(layers_grid)
        self.container.addWidget(w, 1, 1)

        self.trigger_key = KeyWidget()
        self.container.addWidget(QLabel("Trigger"), 2, 0)
        self.container.addWidget(self.trigger_key, 2, 1)

        self.trigger_mods = ModsUI()
        self.container.addWidget(QLabel("Trigger mods"), 3, 0)
        self.container.addWidget(self.trigger_mods, 3, 1)

        self.negative_mods = ModsUI()
        self.container.addWidget(QLabel("Negative mods"), 4, 0)
        self.container.addWidget(self.negative_mods, 4, 1)

        self.suppressed_mods = ModsUI()
        self.container.addWidget(QLabel("Suppressed mods"), 5, 0)
        self.container.addWidget(self.suppressed_mods, 5, 1)

        self.key_replacement = KeyWidget()
        self.container.addWidget(QLabel("Replacement"), 6, 0)
        self.container.addWidget(self.key_replacement, 6, 1)

        self.container.addWidget(QLabel("Options"), 7, 0)
        options_vbox = QVBoxLayout()
        for opt in [
            "Activate when the trigger key is pressed down",
            "Activate when a necessary modifier is pressed down",
            "Activate when a negative modifier is released",
            "Activate on one modifier",
            "Don't deactivate when another key is pressed down",
            "Don't register the trigger key again after the override is deactivated",
        ]:
            options_vbox.addWidget(CheckBoxNoPadding(opt))
        w = QWidget()
        w.setLayout(options_vbox)
        self.container.addWidget(w, 7, 1)

    def widget(self):
        return self.w2

    def load(self, data):
        pass

    def save(self):
        pass

    def on_key_changed(self):
        self.key_changed.emit()


class KeyOverride(BasicEditor):

    def __init__(self):
        super().__init__()
        self.keyboard = None

        self.combo_entries = []
        self.combo_entries_available = []
        self.tabs = TabWidgetWithKeycodes()
        for x in range(128):
            entry = KeyOverrideEntryUI(x)
            entry.key_changed.connect(self.on_key_changed)
            self.combo_entries_available.append(entry)

        self.addWidget(self.tabs)

    def rebuild_ui(self):
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        self.combo_entries = self.combo_entries_available[:self.keyboard.combo_count]
        for x, e in enumerate(self.combo_entries):
            self.tabs.addTab(e.widget(), str(x + 1))
        for x, e in enumerate(self.combo_entries):
            e.load(self.keyboard.combo_get(x))

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.rebuild_ui()

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard and self.device.keyboard.vial_protocol >= 4
                and self.device.keyboard.combo_count > 0)

    def on_key_changed(self):
        for x, e in enumerate(self.combo_entries):
            self.keyboard.combo_set(x, self.combo_entries[x].save())
