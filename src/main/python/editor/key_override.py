# SPDX-License-Identifier: GPL-2.0-or-later
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QSizePolicy, QGridLayout, QVBoxLayout, QLabel, QCheckBox

from widgets.key_widget import KeyWidget
from protocol.key_override import KeyOverrideOptions, KeyOverrideEntry
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

        self.opt_activation_trigger_down = CheckBoxNoPadding("Activate when the trigger key is pressed down")
        self.opt_activation_required_mod_down = CheckBoxNoPadding("Activate when a necessary modifier is pressed down")
        self.opt_activation_negative_mod_up = CheckBoxNoPadding("Activate when a negative modifier is released")
        self.opt_one_mod = CheckBoxNoPadding("Activate on one modifier")
        self.opt_no_reregister_trigger = CheckBoxNoPadding("Don't deactivate when another key is pressed down")
        self.opt_no_unregister_on_other_key_down = CheckBoxNoPadding(
            "Don't register the trigger key again after the override is deactivated")

        for w in [self.opt_activation_trigger_down, self.opt_activation_required_mod_down,
                  self.opt_activation_negative_mod_up, self.opt_one_mod, self.opt_no_reregister_trigger,
                  self.opt_no_unregister_on_other_key_down]:
            w.stateChanged.connect(self.on_change)
            container.addWidget(w)

        self.setLayout(container)

    def on_change(self):
        self.changed.emit()

    def load(self, opt: KeyOverrideOptions):
        self.opt_activation_trigger_down.setChecked(opt.activation_trigger_down)
        self.opt_activation_required_mod_down.setChecked(opt.activation_required_mod_down)
        self.opt_activation_negative_mod_up.setChecked(opt.activation_negative_mod_up)
        self.opt_one_mod.setChecked(opt.one_mod)
        self.opt_no_reregister_trigger.setChecked(opt.no_reregister_trigger)
        self.opt_no_unregister_on_other_key_down.setChecked(opt.no_unregister_on_other_key_down)

    def save(self) -> KeyOverrideOptions:
        opts = KeyOverrideOptions()
        opts.activation_trigger_down = self.opt_activation_trigger_down.isChecked()
        opts.activation_required_mod_down = self.opt_activation_required_mod_down.isChecked()
        opts.activation_negative_mod_up = self.opt_activation_negative_mod_up.isChecked()
        opts.one_mod = self.opt_one_mod.isChecked()
        opts.no_reregister_trigger = self.opt_no_reregister_trigger.isChecked()
        opts.no_unregister_on_other_key_down = self.opt_no_unregister_on_other_key_down.isChecked()
        return opts


class LayersUI(QWidget):

    changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        container = QGridLayout()
        self.layer_chks = [CheckBoxNoPadding(str(x)) for x in range(16)]
        for w in self.layer_chks:
            w.stateChanged.connect(self.on_change)

        for x in range(8):
            container.addWidget(self.layer_chks[x], 0, x)
            container.addWidget(self.layer_chks[x + 8], 1, x)

        self.setLayout(container)

    def load(self, data):
        for x, w in enumerate(self.layer_chks):
            w.setChecked(bool(data & (1 << x)))

    def save(self):
        out = 0
        for x, w in enumerate(self.layer_chks):
            out |= int(w.isChecked()) << x
        return out

    def on_change(self):
        self.changed.emit()


class KeyOverrideEntryUI(QObject):

    changed = pyqtSignal()

    def __init__(self, idx):
        super().__init__()

        self.enable_chk = QCheckBox()
        self.layers = LayersUI()
        self.trigger_key = KeyWidget()
        self.trigger_mods = ModsUI()
        self.negative_mods = ModsUI()
        self.suppressed_mods = ModsUI()
        self.key_replacement = KeyWidget()
        self.options = OptionsUI()

        self.widgets = [self.enable_chk]
        self.enable_chk.stateChanged.connect(self.on_change)
        for w in [self.layers, self.options, self.trigger_key, self.trigger_mods, self.negative_mods,
                  self.suppressed_mods, self.key_replacement]:
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
        self.w2 = QWidget()
        self.w2.setLayout(l)

    def populate_container(self):
        self.container.addWidget(QLabel("Enable"), 0, 0)
        self.container.addWidget(self.enable_chk, 0, 1)

        self.container.addWidget(QLabel("Enable on layers"), 1, 0)
        self.container.addWidget(self.layers, 1, 1)

        self.container.addWidget(QLabel("Trigger"), 2, 0)
        self.container.addWidget(self.trigger_key, 2, 1)

        self.container.addWidget(QLabel("Trigger mods"), 3, 0)
        self.container.addWidget(self.trigger_mods, 3, 1)

        self.container.addWidget(QLabel("Negative mods"), 4, 0)
        self.container.addWidget(self.negative_mods, 4, 1)

        self.container.addWidget(QLabel("Suppressed mods"), 5, 0)
        self.container.addWidget(self.suppressed_mods, 5, 1)

        self.container.addWidget(QLabel("Replacement"), 6, 0)
        self.container.addWidget(self.key_replacement, 6, 1)

        self.container.addWidget(QLabel("Options"), 7, 0)
        self.container.addWidget(self.options, 7, 1)

    def widget(self):
        return self.w2

    def load(self, ko):
        for w in self.widgets:
            w.blockSignals(True)

        self.enable_chk.setChecked(ko.options.enabled)
        self.trigger_key.set_keycode(ko.trigger)
        self.key_replacement.set_keycode(ko.replacement)
        self.layers.load(ko.layers)
        self.trigger_mods.load(ko.trigger_mods)
        self.negative_mods.load(ko.negative_mod_mask)
        self.suppressed_mods.load(ko.suppressed_mods)
        self.options.load(ko.options)

        for w in self.widgets:
            w.blockSignals(False)

    def save(self):
        ko = KeyOverrideEntry()
        ko.options = self.options.save()
        ko.options.enabled = self.enable_chk.isChecked()
        ko.trigger = self.trigger_key.keycode
        ko.replacement = self.key_replacement.keycode
        ko.layers = self.layers.save()
        ko.trigger_mods = self.trigger_mods.save()
        ko.negative_mod_mask = self.negative_mods.save()
        ko.suppressed_mods = self.suppressed_mods.save()
        return ko

    def on_change(self):
        self.changed.emit()


class KeyOverride(BasicEditor):

    def __init__(self):
        super().__init__()
        self.keyboard = None

        self.key_override_entries = []
        self.key_override_entries_available = []
        self.tabs = TabWidgetWithKeycodes()
        for x in range(128):
            entry = KeyOverrideEntryUI(x)
            entry.changed.connect(self.on_change)
            self.key_override_entries_available.append(entry)

        self.addWidget(self.tabs)

    def rebuild_ui(self):
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        self.key_override_entries = self.key_override_entries_available[:self.keyboard.key_override_count]
        for x, e in enumerate(self.key_override_entries):
            self.tabs.addTab(e.widget(), str(x + 1))
        for x, e in enumerate(self.key_override_entries):
            e.load(self.keyboard.key_override_get(x))

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard = device.keyboard
            self.rebuild_ui()

    def valid(self):
        return isinstance(self.device, VialKeyboard) and \
               (self.device.keyboard and self.device.keyboard.vial_protocol >= 4
                and self.device.keyboard.key_override_count > 0)

    def on_change(self):
        for x, e in enumerate(self.key_override_entries):
            self.keyboard.key_override_set(x, self.key_override_entries[x].save())
