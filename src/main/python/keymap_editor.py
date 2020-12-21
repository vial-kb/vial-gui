# SPDX-License-Identifier: GPL-2.0-or-later

from PyQt5.QtWidgets import QVBoxLayout

from keyboard_container import KeyboardContainer
from keycodes import recreate_layer_keycodes
from tabbed_keycodes import TabbedKeycodes
from vial_device import VialKeyboard


class KeymapEditor(QVBoxLayout):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.keyboard_container = KeyboardContainer()
        self.keyboard_container.number_layers_changed.connect(self.on_number_layers_changed)

        self.tabbed_keycodes = TabbedKeycodes()
        self.tabbed_keycodes.keycode_changed.connect(self.on_keycode_changed)

        self.addWidget(self.keyboard_container)
        self.addWidget(self.tabbed_keycodes)

        self.device = None

    def on_number_layers_changed(self):
        recreate_layer_keycodes(self.keyboard_container.keyboard.layers)
        self.tabbed_keycodes.recreate_layer_keycode_buttons()

    def on_keycode_changed(self, code):
        self.keyboard_container.set_key(code)

    def rebuild(self, device):
        self.device = device
        if isinstance(self.device, VialKeyboard):
            self.keyboard_container.rebuild(device.keyboard)

    def valid(self):
        return isinstance(self.device, VialKeyboard)

    def save_layout(self):
        return self.keyboard_container.save_layout()

    def restore_layout(self, data):
        self.keyboard_container.restore_layout(data)
