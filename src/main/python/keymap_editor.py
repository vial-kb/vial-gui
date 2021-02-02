# SPDX-License-Identifier: GPL-2.0-or-later
from any_keycode_dialog import AnyKeycodeDialog
from basic_editor import BasicEditor
from keyboard_container import KeyboardContainer
from keycodes import recreate_keyboard_keycodes
from tabbed_keycodes import TabbedKeycodes
from vial_device import VialKeyboard


class KeymapEditor(BasicEditor):

    def __init__(self, layout_editor):
        super().__init__()

        self.keyboard_container = KeyboardContainer(layout_editor)
        self.keyboard_container.container.anykey.connect(self.on_any_keycode)

        self.tabbed_keycodes = TabbedKeycodes()
        self.tabbed_keycodes.keycode_changed.connect(self.on_keycode_changed)
        self.tabbed_keycodes.anykey.connect(self.on_any_keycode)

        self.addWidget(self.keyboard_container)
        self.addWidget(self.tabbed_keycodes)

        self.device = None

    def on_keycode_changed(self, code):
        self.keyboard_container.set_key(code)

    def rebuild(self, device):
        super().rebuild(device)
        if self.valid():
            self.keyboard_container.rebuild(device.keyboard)
            recreate_keyboard_keycodes(self.keyboard_container.keyboard)
            self.tabbed_keycodes.recreate_keycode_buttons()
            self.keyboard_container.refresh_layer_display()

    def valid(self):
        return isinstance(self.device, VialKeyboard)

    def save_layout(self):
        return self.keyboard_container.save_layout()

    def restore_layout(self, data):
        self.keyboard_container.restore_layout(data)

    def set_keymap_override(self, override):
        self.keyboard_container.set_keymap_override(override)
        self.tabbed_keycodes.set_keymap_override(override)

    def on_any_keycode(self):
        dlg = AnyKeycodeDialog()
        if dlg.exec_() and dlg.value >= 0:
            self.on_keycode_changed(dlg.value)
