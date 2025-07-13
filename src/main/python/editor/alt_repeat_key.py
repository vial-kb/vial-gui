# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QSizePolicy, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QScrollArea, QFrame, QToolButton

from protocol.constants import VIAL_PROTOCOL_DYNAMIC
from util import make_scrollable, tr
from widgets.key_widget import KeyWidget
from protocol.alt_repeat_key import AltRepeatKeyOptions, AltRepeatKeyEntry
from vial_device import VialKeyboard
from editor.basic_editor import BasicEditor
from widgets.checkbox_no_padding import CheckBoxNoPadding
from widgets.tab_widget_keycodes import TabWidgetWithKeycodes


class ModsUI(QWidget):

    changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.mods = [
            CheckBoxNoPadding("LCtrl"),
            CheckBoxNoPadding("LShift"),
            CheckBoxNoPadding("LAlt"),
            CheckBoxNoPadding("LGui"),
            CheckBoxNoPadding("RCtrl"),
            CheckBoxNoPadding("RShift"),
            CheckBoxNoPadding("RAlt"),
            CheckBoxNoPadding("RGui"),
        ]

        for w in self.mods:
            w.stateChanged.connect(self.on_change)

        container = QGridLayout()
        container.addWidget(self.mods[0], 0, 0)
        container.addWidget(self.mods[4], 1, 0)

        container.addWidget(self.mods[1], 0, 1)
        container.addWidget(self.mods[5], 1, 1)

        container.addWidget(self.mods[2], 0, 2)
        container.addWidget(self.mods[6], 1, 2)

        container.addWidget(self.mods[3], 0, 3)
        container.addWidget(self.mods[7], 1, 3)

        self.setLayout(container)

    def load(self, data):
        for x, chk in enumerate(self.mods):
            chk.setChecked(bool(data & (1 << x)))

    def save(self):
        out = 0
        for x, chk in enumerate(self.mods):
            out |= int(chk.isChecked()) << x
        return out

    def on_change(self):
        self.changed.emit()


class OptionsUI(QWidget):

    changed = pyqtSignal()

    def __init__(self):
        super().__init__()

        container = QVBoxLayout()

        self.opt_default_to_this_alt_key = CheckBoxNoPadding("Default to this alt key")
        self.opt_bidirectional = CheckBoxNoPadding("Bidirectional")
        self.opt_ignore_mod_handedness = CheckBoxNoPadding("Ignore mod handedness")

        for w in [self.opt_default_to_this_alt_key, self.opt_bidirectional,
                  self.opt_ignore_mod_handedness]:
            w.stateChanged.connect(self.on_change)
            container.addWidget(w)

        self.setLayout(container)

    def on_change(self):
        self.changed.emit()

    def load(self, opt: AltRepeatKeyOptions):
        self.opt_default_to_this_alt_key.setChecked(opt.default_to_this_alt_key)
        self.opt_bidirectional.setChecked(opt.bidirectional)
        self.opt_ignore_mod_handedness.setChecked(opt.ignore_mod_handedness)

    def save(self) -> AltRepeatKeyOptions:
        opts = AltRepeatKeyOptions()
        opts.default_to_this_alt_key = self.opt_default_to_this_alt_key.isChecked()
        opts.bidirectional = self.opt_bidirectional.isChecked()
        opts.ignore_mod_handedness = self.opt_ignore_mod_handedness.isChecked()
        return opts


class AltRepeatKeyEntryUI(QObject):

    changed = pyqtSignal()

    def __init__(self, idx):
        super().__init__()

        self.enable_chk = QCheckBox()
        self.last_key = KeyWidget()
        self.alt_key = KeyWidget()
        self.allowed_mods = ModsUI()
        self.options = OptionsUI()

        self.widgets = [self.enable_chk]
        self.enable_chk.stateChanged.connect(self.on_change)
        for w in [self.options, self.last_key, self.alt_key, self.allowed_mods]:
            w.changed.connect(self.on_change)
            self.widgets.append(w)

        self.idx = idx
        self.container = QGridLayout()
        self.populate_container()

        w = QWidget()
        w.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        w.setLayout(self.container)
        l = QVBoxLayout()
        l.addWidget(w)
        l.setAlignment(w, QtCore.Qt.AlignHCenter)
        self.w2 = make_scrollable(l)

    def populate_container(self):
        self.container.addWidget(QLabel("Enable"), 0, 0)
        self.container.addWidget(self.enable_chk, 0, 1)

        self.container.addWidget(QLabel("Last key"), 2, 0)
        self.container.addWidget(self.last_key, 2, 1)

        self.container.addWidget(QLabel("Alt key"), 3, 0)
        self.container.addWidget(self.alt_key, 3, 1)

        self.container.addWidget(QLabel("Allowed mods"), 4, 0)
        self.container.addWidget(self.allowed_mods, 4, 1)

        self.container.addWidget(QLabel("Options"), 5, 0)
        self.container.addWidget(self.options, 5, 1)

    def widget(self):
        return self.w2

    def load(self, arep):
        for w in self.widgets:
            w.blockSignals(True)

        self.enable_chk.setChecked(arep.options.enabled)
        self.last_key.set_keycode(arep.keycode)
        self.alt_key.set_keycode(arep.alt_keycode)
        self.allowed_mods.load(arep.allowed_mods)
        self.options.load(arep.options)

        for w in self.widgets:
            w.blockSignals(False)

    def save(self):
        arep = AltRepeatKeyEntry()
        arep.options = self.options.save()
        arep.options.enabled = self.enable_chk.isChecked()
        arep.keycode = self.last_key.keycode
        arep.alt_keycode = self.alt_key.keycode
        arep.allowed_mods = self.allowed_mods.save()
        return arep

    def on_change(self):
        self.changed.emit()


class AltRepeatKey(BasicEditor):

    def __init__(self):
        super().__init__()
        self.keyboard = None

        self.alt_repeat_key_entries = []
        self.alt_repeat_key_entries_available = []
        self.tabs = TabWidgetWithKeycodes()
        for x in range(128):
            entry = AltRepeatKeyEntryUI(x)
            entry.changed.connect(self.on_change)
            self.alt_repeat_key_entries_available.append(entry)

        self.addWidget(self.tabs)

    def rebuild_ui(self):
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        self.alt_repeat_key_entries = self.alt_repeat_key_entries_available[:self.keyboard.alt_repeat_key_count]
        for x, e in enumerate(self.alt_repeat_key_entries):
            self.tabs.addTab(e.widget(), str(x + 1))
        for x, e in enumerate(self.alt_repeat_key_entries):
            e.load(self.keyboard.alt_repeat_key_get(x))

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.rebuild_ui()

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard and self.device.keyboard.vial_protocol >= VIAL_PROTOCOL_DYNAMIC
                and self.device.keyboard.alt_repeat_key_count > 0)

    def on_change(self):
        for x, e in enumerate(self.alt_repeat_key_entries):
            self.keyboard.alt_repeat_key_set(x, self.alt_repeat_key_entries[x].save())
